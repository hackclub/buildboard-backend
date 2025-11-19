from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class RSVP(Base):
    __tablename__ = "rsvps"

    email: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    rsvptime: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
