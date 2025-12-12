from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_auth
from app.schemas.utm import UtmCreate, UtmRead
from app.crud import utms as crud

router = APIRouter(
    prefix="/utms",
    tags=["utms"],
    dependencies=[Depends(verify_auth)],
)


@router.post(
    "",
    response_model=UtmRead,
    status_code=status.HTTP_200_OK,
)
def track_utm(utm_in: UtmCreate, db: Session = Depends(get_db)) -> UtmRead:
    return crud.increment_utm(db, utm_in)
