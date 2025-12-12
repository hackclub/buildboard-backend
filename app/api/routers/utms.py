from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.utm import UTMCreate, UTMRead
from app.models.utm import UTM

router = APIRouter(prefix="/utms", tags=["utms"], dependencies=[Depends(verify_auth)])


@router.post("", response_model=UTMRead, status_code=status.HTTP_200_OK)
def increment_utm(utm_in: UTMCreate, db: Session = Depends(get_db)) -> UTMRead:
    existing = db.get(UTM, utm_in.utm_source)
    
    if existing:
        existing.count += 1
        db.commit()
        db.refresh(existing)
        return existing
    
    new_utm = UTM(utm_source=utm_in.utm_source, count=1)
    db.add(new_utm)
    db.commit()
    db.refresh(new_utm)
    return new_utm
