from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
