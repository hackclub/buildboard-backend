from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VoteBase(BaseModel):
    vote_ranking: int = Field(ge=1)


class VoteCreate(VoteBase):
    user_id: str
    project_id: str


class VoteUpdate(BaseModel):
    vote_ranking: int | None = Field(default=None, ge=1)


class VoteRead(VoteBase):
    vote_id: str
    user_id: str
    project_id: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
