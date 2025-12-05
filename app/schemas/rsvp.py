from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class RSVPBase(BaseModel):
    email: EmailStr
    ip_address: str

class RSVPCreate(RSVPBase):
    pass

class RSVPRead(RSVPBase):
    rsvptime: datetime
    message: str | None = "Success"
    model_config = ConfigDict(from_attributes=True)

class RSVPCollision(BaseModel):
    message: str = "collisions detected"
