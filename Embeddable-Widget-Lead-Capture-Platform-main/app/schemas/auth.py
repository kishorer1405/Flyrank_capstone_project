from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# Register Request
# ============================================================

class RegisterRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    company_name: str = Field(
        min_length=2,
        max_length=120
    )


# ============================================================
# Token Response
# ============================================================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"


# ============================================================
# User Response
# ============================================================

class UserResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    email: EmailStr

    company_name: str