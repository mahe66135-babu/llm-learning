
import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured.")
        return

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a professional customer support assistant.

            Detected intent: {intent}

            Previous conversation summary:
            {summary}

            Instructions:
            - Understand the user's current problem.
            - Use the previous conversation summary.
            - Give clear, practical solutions.
            - Do not claim to perform actions you cannot perform.
            - Never request passwords or authentication codes.
            - Format your response using Markdown.
            """
        ),
        (
            "human",
            "Customer message: {user_message}"
        )
    ])

    parser = StrOutputParser()

    chain = prompt | model | parser

    # Dynamic context
    context = {
        "intent": "account_support",
        "summary": (
            "The customer cannot log into their account. "
            "They tried resetting their password but "
            "have not received the reset email."
        ),
        "user_message": (
            "What should I do next?"
        )
    }

    try:
        response = chain.invoke(context)

        print("\n===== DYNAMIC LANGCHAIN SUPPORT =====")
        print(response)

    except Exception as error:
        print("Application error:", error)


if __name__ == "__main__":
    main()
