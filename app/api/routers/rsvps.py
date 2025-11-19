from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Union
from app.api.deps import get_db, verify_auth
from app.schemas.rsvp import RSVPCreate, RSVPRead, RSVPCollision
from app.crud import rsvps as crud

router = APIRouter(prefix="/rsvps", tags=["rsvps"], dependencies=[Depends(verify_auth)])

@router.post("", response_model=Union[RSVPRead, RSVPCollision], status_code=status.HTTP_200_OK)
def create_rsvp(rsvp_in: RSVPCreate, db: Session = Depends(get_db)):
    return crud.create_rsvp(db, rsvp_in)
