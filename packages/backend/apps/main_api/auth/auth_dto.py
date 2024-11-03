from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator


class LoginDto(BaseModel):
    username: str
    password: str


class RegisterDto(BaseModel):
    username: str
    password: str

    @field_validator('password')
    def validate_password(cls, value):
        if 50 < len(value) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be between 4 and 50 characters long"
            )

        special_characters = "!@#$%^&*()_+[]{}|;:',.<>/?"
        if not any(char in special_characters for char in value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password must contain at least one special character: {special_characters}"
            )
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
