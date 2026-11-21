
import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured.")
        return

    # 1. Connect to Groq
    model = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0.3
    )

    # 2. Create a reusable prompt template
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful Python programming tutor."
        ),
        (
            "human",
            "Explain {topic} in simple language. "
            "Give one practical Python example."
        )
    ])

    # 3. Convert model output into plain text
    parser = StrOutputParser()

    # 4. Connect all components using LCEL
    chain = prompt | model | parser

    # 5. Get user input
    topic = input("Enter a Python topic: ").strip()

    if not topic:
        print("Please enter a topic.")
        return

    # 6. Execute the chain
    try:
        response = chain.invoke({
            "topic": topic
        })

        print("\n===== LANGCHAIN RESPONSE =====")
        print(response)

    except Exception as error:
        print("LangChain application error:", error)


if __name__ == "__main__":
    main()
