from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    pin: str = Field(min_length=4, max_length=6, pattern=r"^\d+$")
    preferred_language: str = "en"


class LoginRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=6, pattern=r"^\d+$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str | None = None
    preferred_language: str

    model_config = {"from_attributes": True}
