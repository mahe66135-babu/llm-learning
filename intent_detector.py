
import os
import instructor

from groq import Groq
from pydantic import BaseModel, Field
from typing import Literal


class IntentResult(BaseModel):
    intent: Literal[
        "account_support",
        "technical_support",
        "general_question"
    ]

    confidence: float = Field(ge=0, le=1)
    reason: str


def detect_intent(client, user_message):
    result = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        response_model=IntentResult,
        messages=[
            {
                "role": "system",
                "content": """
                You are an intent classification assistant.

                Classify the user's message into exactly one category:

                account_support:
                Login, password, account access, registration.

                technical_support:
                Software errors, bugs, application failures.

                general_question:
                General information or questions.

                Return the intent, confidence and a short reason.
                """
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return result


def main():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured.")
        return

    client = instructor.from_groq(
        Groq(api_key=api_key),
        mode=instructor.Mode.JSON
    )

    user_message = input("Enter your message: ").strip()

    if not user_message:
        print("Please enter a message.")
        return

    try:
        result = detect_intent(client, user_message)

        print("\n===== INTENT DETECTION =====")
        print("Intent:", result.intent)
        print("Confidence:", result.confidence)
        print("Reason:", result.reason)

    except Exception as error:
        print("Intent detection failed:", error)


if __name__ == "__main__":
    main()
