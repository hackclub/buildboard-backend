import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.otp import OTP
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.rsvp import RSVP


def generate_otp_code() -> str:
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


def create_otp(db: Session, email: str, expires_minutes: int = 10) -> OTP:
    code = generate_otp_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    otp = OTP(
        email=email.lower(),
        code=code,
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def verify_otp(db: Session, email: str, code: str) -> bool:
    otp = db.query(OTP).filter(
        OTP.email == email.lower(),
        OTP.code == code,
        OTP.used == False,
        OTP.expires_at > datetime.now(timezone.utc)
    ).order_by(OTP.created_at.desc()).first()

    if not otp:
        return False

    otp.used = True
    db.commit()
    return True


def get_or_create_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if user:
        return user

    rsvp = db.get(RSVP, email.lower())

    user = User(email=email.lower())
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.user_id,
        first_name=email.split('@')[0],
        last_name=""
    )
    db.add(profile)

    db.commit()
    db.refresh(user)
    return user


def cleanup_expired_otps(db: Session) -> int:
    result = db.query(OTP).filter(
        OTP.expires_at < datetime.now(timezone.utc)
    ).delete()
    db.commit()
    return result
