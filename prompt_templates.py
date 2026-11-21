def build_support_prompt(
    intent: str,
    summary: str,
    user_message: str
) -> str:

    template = """
You are an AI customer support assistant.

Detected intent:
{intent}

Conversation summary:
{summary}

User's latest message:
{user_message}

Instructions:
- Understand the user's intent.
- Use the conversation summary as context.
- Answer the latest question directly.
- Do not invent information.
- If information is missing, clearly say what is needed.
- Keep the response helpful and concise.
- Never claim that you accessed an account or submitted a support ticket unless an actual tool performed that action.
- Never promise temporary passwords, direct reset links, or account changes.
- Clearly distinguish general guidance from actions actually completed.
- Do not ask users to share their passwords or authentication codes.
- Use the conversation summary to avoid repeating questions already answered.

Generate the final response.
"""

    return template.format(
        intent=intent,
        summary=summary,
        user_message=user_message
    )


def main():

    intent = "account_support"

    summary = (
        "The user is having trouble accessing their account "
        "and wants to reset their password."
    )

    user_message = (
        "I forgot my password. How can I reset it?"
    )

    prompt = build_support_prompt(
        intent,
        summary,
        user_message
    )

    print("===== GENERATED PROMPT =====")
    print(prompt)


if __name__ == "__main__":
    main()