import io
import base64
from urllib.parse import urlencode
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from app.core.config import get_settings


def generate_referral_utm_link(
    referral_code: str,
    campaign: str = "poster",
    source: str = "instagram",
    medium: str = "qr_code",
) -> str:
    settings = get_settings()
    params = {
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    }
    return f"{settings.FRONTEND_URL}/r/{referral_code}?{urlencode(params)}"


def generate_qr_code(
    referral_code: str,
    size: int = 10,
    border: int = 2,
    as_base64: bool = False,
) -> bytes | str:
    url = generate_referral_utm_link(referral_code)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="black",
        back_color="white",
    )
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    if as_base64:
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return buffer.getvalue()


def generate_qr_code_data_uri(referral_code: str) -> str:
    b64 = generate_qr_code(referral_code, as_base64=True)
    return f"data:image/png;base64,{b64}"
