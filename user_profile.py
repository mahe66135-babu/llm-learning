import re

from pydantic import BaseModel, Field, EmailStr, field_validator


class UserProfile(BaseModel):
    name: str = Field(min_length=2)
    age: int = Field(ge=18, le=100)
    email: EmailStr
    pan: str

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

        if not re.fullmatch(pattern, value):
            raise ValueError(
                "PAN must follow the format ABCDE1234F"
            )

        return value


def main():
    user = UserProfile(
        name="Mahesh",
        age=25,
        email="mahesh@example.com",
        pan="ABCDE1234F"
    )

    print("===== VALID USER =====")
    print(user)

    print("\n===== AS DICTIONARY =====")
    print(user.model_dump())

    print("\n===== AS JSON =====")
    print(user.model_dump_json())


if __name__ == "__main__":
    main()