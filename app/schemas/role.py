from pydantic import BaseModel, Field, ConfigDict


class RoleBase(BaseModel):
    role_id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)
