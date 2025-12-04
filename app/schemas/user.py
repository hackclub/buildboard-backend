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
<<<<<<< HEAD
    is_slack_member: bool = False
=======
    is_idv: bool = False
    is_slack_member: bool = False
    is_public: bool = False
    public_profile_url: str | None = None
    bio: str | None = None
>>>>>>> 1eb76e0 (feat: Add all features (handle system, GitHub integration, analytics, migrations, cleanup pycache))


class UserCreate(UserBase):
    handle: str | None = None  # Slack username, used as profile URL handle
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
<<<<<<< HEAD
    is_slack_member: bool | None = None
=======
    is_idv: bool | None = None
    is_slack_member: bool | None = None
    is_public: bool | None = None
    public_profile_url: str | None = None
    bio: str | None = None
    role: str | None = None
    assigned_author_id: str | None = None
    avatar_url: str | None = None


class AuthorInfo(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    slack_id: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    model_config = ConfigDict(from_attributes=True)


class UserPublicRead(BaseModel):
    """Public user info - no sensitive PII exposed"""
    user_id: str
    first_name: str
    last_name: str
    handle: str | None = None
    is_admin: bool = False
    is_reviewer: bool = False
    is_public: bool = False
    public_profile_url: str | None = None
    bio: str | None = None
    role: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
>>>>>>> 1eb76e0 (feat: Add all features (handle system, GitHub integration, analytics, migrations, cleanup pycache))


class UserRead(UserBase):
    """Full user info - only for self or admin"""
    user_id: str
    handle: str | None = None
    public_profile_url: str | None = None
    bio: str | None = None
    role: str | None = None
    assigned_author_id: str | None = None
    avatar_url: str | None = None
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
