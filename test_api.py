
from uuid import uuid4

from fastapi.testclient import TestClient

import api_server

client = TestClient(api_server.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_chat_success(monkeypatch):
    def mock_generate_response(user_message, history=None):
        return f"Test response for: {user_message}"

    monkeypatch.setattr(
        api_server,
        "generate_response",
        mock_generate_response
    )

    response = client.post(
        "/chat",
        json={"message": "Explain Python decorators"}
    )

    assert response.status_code == 200
    assert response.json()["response"] == (
        "Test response for: Explain Python decorators"
    )
    assert response.json()["session_id"]


def test_chat_empty_message():
    response = client.post(
        "/chat",
        json={"message": ""}
    )

    assert response.status_code == 422


def test_chat_missing_message():
    response = client.post(
        "/chat",
        json={}
    )

    assert response.status_code == 422


def test_chat_message_too_long():
    response = client.post(
        "/chat",
        json={"message": "A" * 4001}
    )

    assert response.status_code == 422


def test_chat_invalid_json_type():
    response = client.post(
        "/chat",
        json={"message": 123}
    )

    assert response.status_code == 422


def test_chat_llm_failure(monkeypatch):
    def mock_generate_response(user_message, history=None):
        raise RuntimeError("Simulated LLM service failure")

    monkeypatch.setattr(
        api_server,
        "generate_response",
        mock_generate_response
    )

    response = client.post(
        "/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Unable to generate an AI response. Please try again."
    )


def test_chat_session_continuity(monkeypatch):
    received_histories = []

    def mock_generate_response(user_message, history=None):
        received_histories.append(list(history or []))
        return f"Response to: {user_message}"

    monkeypatch.setattr(
        api_server,
        "generate_response",
        mock_generate_response
    )

    first_response = client.post(
        "/chat",
        json={"message": "My name is Alex"}
    )

    assert first_response.status_code == 200

    session_id = first_response.json()["session_id"]

    second_response = client.post(
        "/chat",
        json={
            "message": "What is my name?",
            "session_id": session_id
        }
    )

    assert second_response.status_code == 200
    assert second_response.json()["session_id"] == session_id

    # The second request should receive the first conversation turn.
    assert len(received_histories[0]) == 0
    assert len(received_histories[1]) == 2
    assert received_histories[1][0].content == "My name is Alex"


def test_clear_conversation(monkeypatch):
    def mock_generate_response(user_message, history=None):
        return "Test response"

    monkeypatch.setattr(
        api_server,
        "generate_response",
        mock_generate_response
    )

    chat_response = client.post(
        "/chat",
        json={"message": "Hello"}
    )

    session_id = chat_response.json()["session_id"]

    clear_response = client.delete(
        f"/chat/{session_id}"
    )

    assert clear_response.status_code == 200
    assert clear_response.json()["status"] == "success"
    assert session_id not in api_server.conversation_store


def test_clear_unknown_conversation():
    unknown_session_id = str(uuid4())

    response = client.delete(
        f"/chat/{unknown_session_id}"
    )

    assert response.status_code == 404


def test_conversation_history_limit(monkeypatch):
    def mock_generate_response(user_message, history=None):
        return f"Response to: {user_message}"

    monkeypatch.setattr(
        api_server,
        "generate_response",
        mock_generate_response
    )

    session_id = str(uuid4())

    # Send six turns (12 messages).
    for number in range(6):
        response = client.post(
            "/chat",
            json={
                "message": f"Message {number + 1}",
                "session_id": session_id
            }
        )

        assert response.status_code == 200

    stored_history = api_server.conversation_store[session_id]

    assert len(stored_history) == api_server.MAX_HISTORY_MESSAGES
    assert len(stored_history) == 10

def test_chat_invalid_markdown(monkeypatch):
    def mock_generate_response(user_message, history=None):
        from markdown_utils import validate_markdown

        response = "```python\nprint('Hello')"

        if not validate_markdown(response):
            raise ValueError("Invalid Markdown")

        return response

    monkeypatch.setattr(
        api_server,
        "generate_response",
        mock_generate_response
    )

    response = client.post(
        "/chat",
        json={"message": "Show me Python code"}
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Unable to generate an AI response. Please try again."
    )