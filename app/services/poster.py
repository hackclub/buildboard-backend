import io
import os
from PIL import Image
from app.services.referral import generate_qr_code


TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "poster_template.png")

QR_X = 775
QR_Y = 1643
QR_SIZE = 220


def generate_referral_poster(
    referral_code: str,
    user_name: str | None = None,
) -> bytes:
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    
    qr_bytes = generate_qr_code(referral_code, size=10, border=1)
    qr_image = Image.open(io.BytesIO(qr_bytes)).convert("RGBA")
    qr_image = qr_image.resize((QR_SIZE, QR_SIZE), Image.Resampling.LANCZOS)
    
    template.paste(qr_image, (QR_X, QR_Y))
    
    output = template.convert("RGB")
    buffer = io.BytesIO()
    output.save(buffer, format="PNG", quality=95)
    buffer.seek(0)
    return buffer.getvalue()
