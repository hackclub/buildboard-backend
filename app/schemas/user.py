from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    slack_id: str = Field(min_length=1, max_length=64)
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    slack_id: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
