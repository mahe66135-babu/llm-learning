import os
from groq import Groq

def main():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured.")
        return
    client = Groq(api_key = api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "your are a helpful for python tutor."
            },
            {
                "role": "user",
                "content":"Explain Python tuples and Lists with examples."
            }
        ],
         max_completion_tokens=500
    )

    print("===== MODEL =====")
    print(response.model)

    print("\n===== GROQ RESPONSE =====")
    print(response.choices[0].message.content)

    print("\n===== USAGE ======")
    print(response.usage)


if __name__ == "__main__":
    main()