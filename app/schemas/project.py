from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class ProjectBase(BaseModel):
    project_name: str = Field(min_length=1, max_length=200)
    project_description: str = Field(min_length=1)
    project_type: str | None = None
    attachment_urls: list[str] | None = None
    code_url: str | None = None
    live_url: str | None = None
    submission_week: str = Field(min_length=1, max_length=50)
    paper_url: str | None = None
    shipped: bool = False
    sent_to_airtable: bool = False
    review_ids: list[str] | None = None
    hackatime_project_keys: list[str] | None = None
    time_spent: int | None = Field(default=None, ge=0)


class ProjectCreate(ProjectBase):
    user_id: str


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(default=None, max_length=200)
    project_description: str | None = None
    project_type: str | None = None
    attachment_urls: list[str] | None = None
    code_url: str | None = None
    live_url: str | None = None
    submission_week: str | None = Field(default=None, max_length=50)
    paper_url: str | None = None
    shipped: bool | None = None
    sent_to_airtable: bool | None = None
    review_ids: list[str] | None = None
    hackatime_project_keys: list[str] | None = None
    time_spent: int | None = Field(default=None, ge=0)


class ProjectRead(ProjectBase):
    project_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
