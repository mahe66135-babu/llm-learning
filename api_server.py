
import os
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime
from markdown_utils import validate_markdown


# Create FastAPI application
app = FastAPI(
    title="LLM Customer Support API",
    description="Customer support API powered by LangChain and Groq",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory conversation storage
conversation_store = {}
conversation_timestamps = {}

MAX_HISTORY_MESSAGES = 10


# Request model
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None


# Response model
class ChatResponse(BaseModel):
    response: str
    session_id: str


# Generate AI response with conversation context
def generate_response(user_message: str, history=None):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a helpful AI customer support assistant.

            Instructions:
            - Give accurate and practical answers.
            - Use previous conversation messages when relevant.
            - Format your response using Markdown.
            - Use headings, bullet points and tables when useful.
            - Use Markdown code blocks for programming examples.
            - Never invent company policies, phone numbers or email addresses.
            - Never request passwords or authentication codes.
            - Do not claim to perform actions you cannot perform.
            """
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_message}")
    ])

    chain = prompt | model | StrOutputParser()

    response = chain.invoke({
    "history": history or [],
    "user_message": user_message
})
    if not validate_markdown(response):
        raise ValueError("AI generated invalid Markdown response.")
    return response



# Health-check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "LLM API is running!"
    }


# Customer support endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    session_id = request.session_id or str(uuid4())

    history = conversation_store.get(session_id, [])

    try:
        response = generate_response(
            request.message,
            history
        )

        # Save conversation only after successful response
        updated_history = history + [
            HumanMessage(content=request.message),
            AIMessage(content=response)
        ]

        conversation_store[session_id] = updated_history[
            -MAX_HISTORY_MESSAGES:
        ]
        updated_timestamps = conversation_timestamps.get(
    session_id, []
) + [
    datetime.now().astimezone().isoformat(),
    datetime.now().astimezone().isoformat()
]
        conversation_timestamps[session_id] = updated_timestamps[
    -MAX_HISTORY_MESSAGES:
]

        return ChatResponse(
            response=response,
            session_id=session_id
        )

    except Exception as error:
        print("LLM API error:", error)

        raise HTTPException(
            status_code=502,
            detail="Unable to generate an AI response. Please try again."
        )



@app.get("/chat/{session_id}/history")
def get_conversation_history(session_id: str):

    history = conversation_store.get(session_id)

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    timestamps = conversation_timestamps.get(session_id, [])

    messages = []

    for index, message in enumerate(history):

        role = (
            "user"
            if isinstance(message, HumanMessage)
            else "assistant"
        )

        timestamp = (
            timestamps[index]
            if index < len(timestamps)
            else None
        )

        messages.append({
            "role": role,
            "content": message.content,
            "timestamp": timestamp
        })

    return {
        "session_id": session_id,
        "messages": messages
    }


# Clear conversation history
@app.delete("/chat/{session_id}")
def clear_conversation(session_id: str):

    if session_id not in conversation_store:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    del conversation_store[session_id]
    conversation_timestamps.pop(session_id, None)

    return {
        "status": "success",
        "message": "Conversation history cleared."
    }
