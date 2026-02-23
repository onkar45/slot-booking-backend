from pydantic import BaseModel, field_validator
from datetime import date, time, datetime

class SlotCreate(BaseModel):
    date: date
    start_time: time
    end_time: time

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v < date.today():
            raise ValueError('Date cannot be in the past')
        return v

    @field_validator('end_time')
    @classmethod
    def validate_time(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v

class SlotResponse(BaseModel):
    id: int
    date: date
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True