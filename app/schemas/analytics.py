from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class OnboardingEventCreate(BaseModel):
    userId: str
    event: Literal['onboarding_started', 'onboarding_next', 'onboarding_skip', 'onboarding_completed']
    slide: int | None = None
    totalSlides: int | None = None
    completedAt: str | None = None
    timestamp: str


class OnboardingEventRead(BaseModel):
    id: str
    user_id: str
    event: str
    slide: int | None
    total_slides: int | None
    completed_at: datetime | None
    timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
