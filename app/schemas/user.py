from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserProfilePublic(BaseModel):
    """Public profile - NO PII (no names, no birthday)"""
    avatar_url: str | None = None
    bio: str | None = None
    is_public: bool = False
    model_config = ConfigDict(from_attributes=True)


class UserProfileCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = None
    bio: str | None = None
    is_public: bool = False
    birthday: datetime | None = None


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = None
    bio: str | None = None
    is_public: bool | None = None
    birthday: datetime | None = None


class UserAddressCreate(BaseModel):
    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    post_code: str | None = Field(default=None, max_length=20)
    is_primary: bool = True


class UserAddressUpdate(BaseModel):
    address_line_1: str | None = Field(default=None, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    post_code: str | None = Field(default=None, max_length=20)
    is_primary: bool | None = None


class RoleRead(BaseModel):
    role_id: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserRoleRead(BaseModel):
    role_id: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    slack_id: str | None = Field(default=None, max_length=64)
    handle: str | None = Field(default=None, max_length=50)
    profile: UserProfileCreate
    address: UserAddressCreate | None = None


class UserUpdate(BaseModel):
    slack_id: str | None = Field(default=None, max_length=64)
    handle: str | None = Field(default=None, max_length=50)


class UserPublicRead(BaseModel):
    """Public user info - NO PII exposed"""
    user_id: str
    handle: str | None = None
    profile: UserProfilePublic | None = None
    roles: list[UserRoleRead] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserSelfRead(BaseModel):
    """User reading their own info - includes some PII they need"""
    user_id: str
    handle: str | None = None
    referral_code: str
    profile: UserProfilePublic | None = None
    roles: list[UserRoleRead] = []
    has_address: bool = False
    storyline_completed_at: datetime | None = None
    hackatime_completed_at: datetime | None = None
    slack_linked_at: datetime | None = None
    idv_completed_at: datetime | None = None
    onboarding_completed_at: datetime | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserExistsResponse(BaseModel):
    exists: bool


class LoginRecordedResponse(BaseModel):
    message: str
    logged_in_at: str
