from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import String, DateTime, func, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    slack_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_reviewer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_idv: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_slack_member: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    post_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    birthday: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dates_logged_in: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    hackatime_projects: Mapped[list["HackatimeProject"]] = relationship("HackatimeProject", back_populates="user", cascade="all, delete-orphan")
