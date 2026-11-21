import os
import re

import instructor
from groq import Groq
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator
from instructor.v2.core.errors import InstructorRetryException
from typing import Optional


class UserProfile(BaseModel):
    name: str = Field(min_length=2)
    age: int = Field(ge=18, le=100)
    email: Optional[EmailStr] = None
    pan: Optional[str] = None

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid PAN format")

        return value


def create_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    return instructor.from_groq(
        Groq(api_key=api_key),
        mode=instructor.Mode.JSON
    )


def extract_user_profile(client, text: str) -> UserProfile:
    return client.chat.completions.create(
        model="openai/gpt-oss-20b",
        response_model=UserProfile,
        max_retries=2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract user information from the user's text. "
                    "Return only information explicitly provided by the user. "
                    "Never invent, guess, or modify personal information."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )


def main():

    try:
        client = create_client()

        text = (
     "My name is Mahesh and I am 25 years old."
)

        user = extract_user_profile(client, text)

        print("===== SUCCESS =====")
        print(f"Name  : {user.name}")
        print(f"Age   : {user.age}")
        print(f"Email : {user.email}")
        print(f"PAN   : {user.pan}")

        print("\n===== JSON =====")
        print(user.model_dump_json(indent=2))

    except InstructorRetryException:
        print("ERROR: LLM could not produce valid structured data.")

    except ValidationError as error:
        print("ERROR: Validation failed.")

        for item in error.errors():
            print(f"- {item['loc'][0]}: {item['msg']}")

    except Exception as error:
        print(f"ERROR: {error}")


if __name__ == "__main__":
    main()