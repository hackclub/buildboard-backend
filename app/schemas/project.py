from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class ProjectBase(BaseModel):
    project_name: str = Field(min_length=1, max_length=200)
    project_description: str = Field(min_length=1)
    attachment_urls: list[str] | None = None
    code_url: str | None = None
    live_url: str | None = None
    submission_week: int = Field(ge=1)
    paper_url: str | None = None


class ProjectCreate(ProjectBase):
    user_id: str


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(default=None, max_length=200)
    project_description: str | None = None
    attachment_urls: list[str] | None = None
    code_url: str | None = None
    live_url: str | None = None
    submission_week: int | None = Field(default=None, ge=1)
    paper_url: str | None = None


class ProjectRead(ProjectBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
