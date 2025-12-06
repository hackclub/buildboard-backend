from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_description: Mapped[str] = mapped_column(Text, nullable=False)
    project_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    attachment_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    code_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    paper_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    submission_week: Mapped[str] = mapped_column(String(50), nullable=False)
    shipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_to_airtable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    github_installation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    github_repo_path: Mapped[str | None] = mapped_column(String(200), nullable=True)
    time_spent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="projects")
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="project", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="project", cascade="all, delete-orphan")
    hackatime_links: Mapped[list["ProjectHackatimeLink"]] = relationship("ProjectHackatimeLink", back_populates="project", cascade="all, delete-orphan")
