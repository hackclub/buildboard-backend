import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.rsvp import RSVP
from app.schemas.rsvp import RSVPCreate

logger = logging.getLogger(__name__)

def create_rsvp(db: Session, data: RSVPCreate):
    # Check if email already exists
    existing_rsvp = db.get(RSVP, data.email)
    if existing_rsvp:
        return {"message": "collisions detected"}

    rsvp = RSVP(**data.model_dump())
    db.add(rsvp)
    db.commit()
    db.refresh(rsvp)
    logger.info(f"New RSVP created: {rsvp.email}")
    return rsvp

def get_rsvp(db: Session, email: str) -> RSVP | None:
    return db.get(RSVP, email)

def get_ip_count(db: Session, ip_address: str) -> int:
    return db.query(func.count(RSVP.email)).filter(RSVP.ip_address == ip_address).scalar()
