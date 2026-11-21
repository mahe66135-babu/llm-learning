
import os

import instructor
from groq import Groq, APIError

from prompt_templates import build_support_prompt
from context_builder import build_context
from intent_detector import detect_intent
from conversation_summarizer import summarize_conversation


def generate_response(client, context):
    prompt = build_support_prompt(
        intent=context["intent"],
        summary=context["summary"],
        user_message=context["user_message"]
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI customer support assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_completion_tokens=500
    )

    return response.choices[0].message.content


def main():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured.")
        return

    groq_client = Groq(api_key=api_key)

    structured_client = instructor.from_groq(
        groq_client,
        mode=instructor.Mode.JSON
    )

    # Stores messages while this application is running
    conversation_history = []

    print("\n===== AI CUSTOMER SUPPORT =====")
    print("Type 'exit' to stop the conversation.")

    while True:
        user_message = input("\nYou: ").strip()

        if user_message.lower() == "exit":
            print("Conversation ended.")
            break

        if not user_message:
            print("Please enter a message.")
            continue

        try:
            # Step 1: Detect intent
            intent_result = detect_intent(
                structured_client,
                user_message
            )

            print("\nDetected intent:", intent_result.intent)
            print("Confidence:", intent_result.confidence)

            # Step 2: Check confidence
            if intent_result.confidence < 0.60:
                print("I'm not sure I understand. Could you clarify?")
                continue

            # Step 3: Summarize previous conversation
            recent_history = conversation_history[-10:]
            summary = summarize_conversation(
                groq_client,
                recent_history
            )

            print("\n===== CONVERSATION SUMMARY =====")
            print(summary)

            # Step 4: Build context
            context = build_context(
                intent=intent_result.intent,
                summary=summary,
                user_message=user_message
            )

            # Step 5: Generate response
            answer = generate_response(
                groq_client,
                context
            )

            print("\nAI Assistant:", answer)

            # Step 6: Save this turn for future summaries
            conversation_history.append({
                "role": "user",
                "content": user_message
            })

            conversation_history.append({
                "role": "assistant",
                "content": answer
            })

        except APIError as error:
            print("Groq API error:", error)

        except Exception as error:
            print("Application error:", error)


if __name__ == "__main__":
    main()
