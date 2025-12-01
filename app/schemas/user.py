from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    slack_id: str | None = Field(default=None, max_length=64)
    email: EmailStr
    is_admin: bool = False
    is_reviewer: bool = False
    is_idv: bool = False
    is_idv: bool = False
    is_slack_member: bool = False
    is_public: bool = False


class UserCreate(UserBase):
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    post_code: str | None = None
    birthday: datetime | None = None


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    slack_id: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    is_admin: bool | None = None
    is_reviewer: bool | None = None
    is_idv: bool | None = None
    is_idv: bool | None = None
    is_slack_member: bool | None = None
    is_public: bool | None = None


class UserRead(UserBase):
    user_id: str
    handle: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    post_code: str | None = None
    birthday: datetime | None = None
    dates_logged_in: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
