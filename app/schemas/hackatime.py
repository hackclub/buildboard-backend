from pydantic import BaseModel
from datetime import datetime

class HackatimeProjectBase(BaseModel):
    name: str
    seconds: int

class HackatimeProject(HackatimeProjectBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HackatimeProjectList(BaseModel):
    projects: list[HackatimeProject]
