# import tiktoken

# def main():
#     text = "Hello, My name is Mahesh and I am learning LLM application development."

#     encoding = tiktoken.get_encoding("cl100k_base")

#     tokens = encoding.encode(text)

#     print("====== TEXT =======")
#     print(text)

#     print("\n====== TOKEN ======")
#     print(tokens)

#     print("\n====== TOKEN COUNT ======")
#     print(len(tokens))

#     print("\n======DECODE TOKENS =======")

#     for token in tokens:
#         print(token, "->", repr(encoding.decode([token])))



# if __name__ == "__main__":
#     main()

import tiktoken


def count_tokens(text, encoding):
    return len(encoding.encode(text))


def main():
    encoding = tiktoken.get_encoding("cl100k_base")

    prompts = {
        "Short": "Explain Python.",
        
        "Medium": (
            "Explain Python lists and dictionaries "
            "with simple examples for a beginner."
        ),

        "Long": (
            "You are a professional Python instructor. "
            "Explain Python lists and dictionaries in detail. "
            "Compare their characteristics, explain how they are "
            "created and modified, provide practical examples, "
            "discuss common mistakes beginners make, and explain "
            "when a developer should choose a list versus a dictionary."
        )
    }

    print("===== TOKEN COMPARISON =====")

    for name, text in prompts.items():
        count = count_tokens(text, encoding)

        print(f"\n{name}")
        print(f"Text: {text}")
        print(f"Token count: {count}")


if __name__ == "__main__":
    main()