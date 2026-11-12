from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    username:str = Field(min_length=3, max_length=20)
    email: EmailStr = Field(max_length=320)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: str | None
    alert_type: str | None
    message: str | None
    acknowledged: int
