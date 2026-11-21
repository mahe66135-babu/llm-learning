def build_context(
        intent: str,
        summary: str,
        user_message: str
)-> dict:


    return {
        "intent": intent,
        "summary": summary,
        "user_message": user_message
    }

def main():

    context = build_context(
        intent="technical_support",
        summary="The user is unable to log into the application.",
        user_message="The login button keeps showing an error."
    )

    print("===== CONTEXT =====")

    for key, value in context.items():
        print(f"{key}:{value}")


if __name__== "__main__":
    main()