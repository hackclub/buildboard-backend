from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.auth import SendOTPRequest, VerifyOTPRequest, AuthResponse
from app.crud import auth as auth_crud
from app.services.email import send_otp_email

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(verify_auth)])


@router.post("/send-otp", response_model=AuthResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    otp = auth_crud.create_otp(db, request.email)
    
    email_sent = send_otp_email(request.email, otp.code)
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )
    
    return AuthResponse(message="OTP sent")


@router.post("/verify-otp", response_model=AuthResponse)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    is_valid = auth_crud.verify_otp(db, request.email, request.otp)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired code"
        )
    
    user = auth_crud.get_or_create_user_by_email(db, request.email)
    
    return AuthResponse(message="Verified", userID=user.user_id)
