from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class OnboardingEvent(Base):
    __tablename__ = "onboarding_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event: Mapped[str] = mapped_column(String(50), nullable=False)
    slide: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_slides: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
