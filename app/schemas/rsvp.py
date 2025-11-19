from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class RSVPBase(BaseModel):
    email: EmailStr

class RSVPCreate(RSVPBase):
    pass

class RSVPRead(RSVPBase):
    rsvptime: datetime
    model_config = ConfigDict(from_attributes=True)
