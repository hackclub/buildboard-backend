from datetime import datetime
from uuid import uuid4
import secrets
import string
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


def generate_referral_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    slack_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    handle: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    referral_code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False, default=generate_referral_code, index=True)
    referred_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    storyline_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hackatime_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    slack_linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    idv_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    addresses: Mapped[list["UserAddress"]] = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    login_events: Mapped[list["UserLoginEvent"]] = relationship("UserLoginEvent", back_populates="user", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    hackatime_projects: Mapped[list["HackatimeProject"]] = relationship("HackatimeProject", back_populates="user", cascade="all, delete-orphan")
    referrer: Mapped["User"] = relationship("User", remote_side=[user_id], foreign_keys=[referred_by_user_id])
