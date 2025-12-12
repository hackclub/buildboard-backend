from pydantic import BaseModel


class UTMCreate(BaseModel):
    utm_source: str


class UTMRead(BaseModel):
    utm_source: str
    count: int

    class Config:
        from_attributes = True
