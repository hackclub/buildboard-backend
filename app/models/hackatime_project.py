from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class HackatimeProject(Base):
    __tablename__ = "hackatime_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="hackatime_projects")
    project_links: Mapped[list["ProjectHackatimeLink"]] = relationship("ProjectHackatimeLink", back_populates="hackatime_project", cascade="all, delete-orphan")
