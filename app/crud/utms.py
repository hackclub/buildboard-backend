from sqlalchemy.orm import Session
from app.models.utm import Utm
from app.schemas.utm import UtmCreate


def increment_utm(db: Session, data: UtmCreate) -> Utm:
    utm = db.get(Utm, data.utm_source)
    if utm:
        utm.count += 1
    else:
        utm = Utm(utm_source=data.utm_source, count=1)
        db.add(utm)

    db.commit()
    db.refresh(utm)
    return utm
