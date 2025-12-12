from enum import IntEnum
from pydantic import BaseModel, Field


class VisibilityLevel(IntEnum):
    HIDDEN = 1
    LOCAL = 2
    COMMUNITY = 3
    FEATURED = 4
    BILLBOARD = 5


class VisibilityMilestone(BaseModel):
    id: str
    name: str
    description: str
    completed: bool
    level: int


class VisibilityStatus(BaseModel):
    current_level: int = Field(ge=1, le=5)
    current_level_name: str
    next_level: int | None = Field(default=None, ge=1, le=5)
    next_level_name: str | None = None
    progress_percentage: int = Field(ge=0, le=100)
    milestones: list[VisibilityMilestone]
    total_completed: int
    total_milestones: int
