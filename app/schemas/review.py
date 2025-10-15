from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReviewBase(BaseModel):
    review_comments: str = Field(min_length=1)
    review_decision: str = Field(min_length=1, max_length=50)


class ReviewCreate(ReviewBase):
    reviewer_user_id: str
    project_id: str


class ReviewUpdate(BaseModel):
    review_comments: str | None = None
    review_decision: str | None = Field(default=None, max_length=50)


class ReviewRead(ReviewBase):
    review_id: str
    reviewer_user_id: str
    project_id: str
    review_timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
