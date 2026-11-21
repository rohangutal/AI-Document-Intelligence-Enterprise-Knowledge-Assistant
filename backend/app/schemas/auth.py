"""Authentication API schemas."""

from uuid import UUID

import re

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    full_name: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=8, max_length=256)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("A valid email address is required")
        return value.lower()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
