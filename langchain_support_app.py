import os
import instructor

from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from intent_detector import detect_intent
from conversation_summarizer import summarize_conversation
from context_builder import build_context

def main():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured")
        return

    groq_client = Groq(api_key=api_key)

    instructor_client = instructor.from_groq(
        groq_client,
        mode=instructor.Mode.JSON
    )

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a Professional customer support assistant.
            
            Customer_intent:{intent}

            Conversation summary:
            {summary}

            Rules:
            -Answer based on the provide context.
            -Give clear and practical suggestions.
            -Never invent company policies, email addresses,
            phone numbers, links, or supported services.
            -If company-specific information is Unavailable,
            clearly say so.
            -Never request password or authentication codes.
            -Do not claim to perform actions you cannot perform.
            -Format responses using Markdown.
            """
        ),
        (
            "human",
            "{user_message}"
        )
    ])

    parser = StrOutputParser()

    chain = prompt | model | parser

    conversation_history = []

    print("\n======= LANGCHAIN CUSTOMER SUPPORT=========")
    print("Type 'exit' to stop.\n")

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() == "exit":
            print("Assistant: Goodbye!")
            break
        if not user_message:
            print("Please enter a message.")
            continue

        try:
            intent_result = detect_intent(
                instructor_client,
                user_message
            )

            print("\nDetected intent:", intent_result.intent)
            print("Confidence:", intent_result.confidence)

            if intent_result.confidence<0.60:
                print(
                    "Assistant: Could you clarify your question?"
                )
                continue

            summary = summarize_conversation(
                groq_client,
                conversation_history[-10:]
            )

            context = build_context(
                intent=intent_result.intent,
                summary=summary,
                user_message=user_message
            )

            response = chain.invoke(context)

            print("\nAssistant:",response)

            conversation_history.append({
                "role": "user",
                "content": user_message
            })

            conversation_history.append({
                "role": "assistant",
                "content": response
            })

        except Exception as error:
            print("\nApplication error:", error)



if __name__ =="__main__":
    main()

