
import json


def summarize_conversation(client, conversation_history):

    if not conversation_history:
        return "No previous conversation history is available."

    history_text = json.dumps(
        conversation_history,
        indent=2
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": 
"""
You are a precise conversation summarization assistant.

Summarize the complete conversation history.

IMPORTANT RULES:
- Read every message before writing the summary.
- Preserve all facts explicitly stated by the user.
- Never say the user has not done something if they
  explicitly said they did it.
- Distinguish between actions suggested by the assistant
  and actions actually completed by the user.
- Preserve unresolved problems.
- Do not invent information.

Include:
1. Main issue.
2. Details confirmed by the user.
3. Actions suggested by the assistant.
4. Actions actually completed by the user.
5. Remaining unresolved issue.

Keep the summary concise and accurate.
"""

            },
            {
                "role": "user",
                "content": history_text
            }
        ],
        max_completion_tokens=250
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    import os
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured.")
    else:
        client = Groq(api_key=api_key)

        # Sample conversation history
        conversation_history = [
            {
                "role": "user",
                "content": "I cannot log into my account."
            },
            {
                "role": "assistant",
                "content": "Are you receiving any error message?"
            },
            {
                "role": "user",
                "content": "It says my password is incorrect."
            },
            {
                "role": "assistant",
                "content": "You can try the Forgot Password option."
            },
            {
                "role": "user",
                "content": "I tried it, but I haven't received the reset email."
            }
        ]

        try:
            summary = summarize_conversation(
                client,
                conversation_history
            )

            print("\n===== CONVERSATION SUMMARY =====")
            print(summary)

        except Exception as error:
            print("Summarization failed:", error)
