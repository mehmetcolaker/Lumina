import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Request schema for user registration.

    Attributes:
        email: The new user's email address.
        password: The new user's password (plain-text, min 8 chars).
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Response schema representing a public user profile.

    Attributes:
        id: The user's UUID.
        email: The user's email address.
        is_active: Whether the account is active.
        is_premium: Whether the user has premium access.
        created_at: Account creation timestamp.
    """

    id: uuid.UUID
    email: str
    is_active: bool
    is_premium: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Response schema returned after a successful login.

    Attributes:
        access_token: The signed JWT string.
        token_type: The token type (always "Bearer").
    """

    access_token: str
    token_type: str = "Bearer"


class TokenPayload(BaseModel):
    """Payload extracted from a decoded JWT.

    Attributes:
        sub: The subject claim (user UUID string).
    """

    sub: str | None = None
