from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    reviewer_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.project_id"), nullable=False, index=True)
    review_comments: Mapped[str] = mapped_column(Text, nullable=False)
    review_decision: Mapped[str] = mapped_column(String(50), nullable=False)
    review_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    reviewer: Mapped["User"] = relationship("User")
    project: Mapped["Project"] = relationship("Project", back_populates="reviews")
