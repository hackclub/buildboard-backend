from pydantic import BaseModel, ConfigDict


class UtmBase(BaseModel):
    utm_source: str


class UtmCreate(UtmBase):
    pass


class UtmRead(UtmBase):
    count: int
    model_config = ConfigDict(from_attributes=True)
