from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.rsvp import RSVPCreate, RSVPRead
from app.crud import rsvps as crud

router = APIRouter(prefix="/rsvps", tags=["rsvps"], dependencies=[Depends(verify_auth)])

@router.post("", response_model=RSVPRead, status_code=status.HTTP_201_CREATED)
def create_rsvp(rsvp_in: RSVPCreate, db: Session = Depends(get_db)) -> RSVPRead:
    return crud.create_rsvp(db, rsvp_in)
