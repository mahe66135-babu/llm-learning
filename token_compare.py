import os
import tiktoken

from groq import Groq


def main():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured")
        return

    system_message = "You are a helpful Tutor."

    user_message = (
        "Explain python Lists and Dictionaries"
        "with simple example for a beginning."
    )

    encoding = tiktoken.get_encoding("cl100k_base")

    system_tokens = len(encoding.encode(system_message))
    user_tokens = len(encoding.encode(user_message))

    print("====== TIKTOKEN ESTIMATE ======")
    print(f"System tokens: {system_tokens}")
    print(f"User tokens: {user_tokens}")
    print(f"Estimated total: {system_tokens + user_tokens}")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role":"system",
                "content": system_message
            },
            {
                "role":"user",
                "content": user_message
            }

        ],
        max_completion_tokens=500
    )

    print("\n=======GROQ USAGE ========")
    print(response.usage)


if __name__ == "__main__":
    main()
    