from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.rsvp import RSVP
from app.schemas.rsvp import RSVPCreate

def create_rsvp(db: Session, data: RSVPCreate):
    # Check if email already exists
    existing_rsvp = db.get(RSVP, data.email)
    if existing_rsvp:
        return {"message": "collisions detected"}

    # Check IP address count
    ip_count = db.query(func.count(RSVP.email)).filter(RSVP.ip_address == data.ip_address).scalar()
    if ip_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many RSVPs from this IP address"
        )

    rsvp = RSVP(**data.model_dump())
    db.add(rsvp)
    db.commit()
    db.refresh(rsvp)
    print(f"New RSVP created: {rsvp.email}")
    return rsvp

def get_rsvp(db: Session, email: str) -> RSVP | None:
    return db.get(RSVP, email)
