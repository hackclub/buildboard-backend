import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_otp_email(to_email: str, otp_code: str) -> bool:
    settings = get_settings()
    
    if not settings.SMTP_HOST:
        logger.warning(f"SMTP not configured. OTP for {to_email}: {otp_code}")
        return True
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your BuildBoard login code: {otp_code}"
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = to_email

        text = f"""
Your BuildBoard login code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, you can safely ignore this email.
"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0e305b; color: white; padding: 40px; }}
        .container {{ max-width: 500px; margin: 0 auto; background: #1a365d; border: 2px solid white; padding: 40px; text-align: center; }}
        h1 {{ margin: 0 0 20px 0; font-size: 24px; }}
        .code {{ font-size: 36px; font-weight: bold; letter-spacing: 8px; margin: 30px 0; padding: 20px; background: rgba(255,255,255,0.1); }}
        p {{ color: rgba(255,255,255,0.75); margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Your login code</h1>
        <div class="code">{otp_code}</div>
        <p>This code will expire in 10 minutes.</p>
        <p>If you didn't request this code, you can safely ignore this email.</p>
    </div>
</body>
</html>
"""

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], to_email, msg.as_string())
        
        logger.info(f"OTP email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {to_email}: {e}")
        return False
