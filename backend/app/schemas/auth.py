import uuid

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    real_name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserBrief(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    real_name: str | None
    role: str
    tenant_id: uuid.UUID
    department_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBrief
