from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.rsvp import RSVP
from app.schemas.rsvp import RSVPCreate

def create_rsvp(db: Session, data: RSVPCreate) -> RSVP:
    rsvp = RSVP(**data.model_dump())
    db.add(rsvp)
    try:
        db.commit()
        db.refresh(rsvp)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already RSVP'd"
        )
    return rsvp

def get_rsvp(db: Session, email: str) -> RSVP | None:
    return db.get(RSVP, email)
