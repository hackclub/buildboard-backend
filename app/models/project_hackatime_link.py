from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class ProjectHackatimeLink(Base):
    __tablename__ = "project_hackatime_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.project_id"), nullable=False, index=True)
    hackatime_project_id: Mapped[str] = mapped_column(String(36), ForeignKey("hackatime_projects.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="hackatime_links")
    hackatime_project: Mapped["HackatimeProject"] = relationship("HackatimeProject", back_populates="project_links")

    __table_args__ = (
        UniqueConstraint("project_id", "hackatime_project_id", name="uq_project_hackatime"),
    )
