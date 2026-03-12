from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional

class BlockedDateCreate(BaseModel):
    date: date
    reason: Optional[str] = None

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v < date.today():
            raise ValueError('Cannot block past dates')
        return v

class BlockedDateResponse(BaseModel):
    id: int
    date: date
    reason: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class BlockedDateWithCreator(BaseModel):
    id: int
    date: date
    reason: Optional[str]
    created_by: int
    created_at: datetime
    creator: dict

    class Config:
        from_attributes = True
