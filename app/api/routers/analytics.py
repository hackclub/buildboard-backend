from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.analytics import OnboardingEventCreate, OnboardingEventRead
from app.models.onboarding_event import OnboardingEvent

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(verify_auth)])


@router.post("/onboarding", response_model=OnboardingEventRead, status_code=status.HTTP_201_CREATED)
def track_onboarding(event_in: OnboardingEventCreate, db: Session = Depends(get_db)) -> OnboardingEventRead:
    completed_at = None
    if event_in.completedAt:
        try:
            completed_at = datetime.fromisoformat(event_in.completedAt.replace('Z', '+00:00'))
        except ValueError:
            pass

    timestamp = datetime.fromisoformat(event_in.timestamp.replace('Z', '+00:00'))

    db_event = OnboardingEvent(
        user_id=event_in.userId,
        event=event_in.event,
        slide=event_in.slide,
        total_slides=event_in.totalSlides,
        completed_at=completed_at,
        timestamp=timestamp
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event
