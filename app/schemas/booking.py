from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, date, time
from typing import Optional

class UserInfo(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    date: date
    start_time: time
    duration_minutes: int
    
    @field_validator('duration_minutes')
    @classmethod
    def validate_duration(cls, v):
        # Allow 30, 60, 90, or 120 minute bookings
        allowed_durations = [30, 60, 90, 120]
        if v not in allowed_durations:
            raise ValueError(f'Duration must be one of {allowed_durations} minutes')
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        from datetime import date as dt_date
        if v < dt_date.today():
            raise ValueError('Cannot book for past dates')
        return v

class BookingResponse(BaseModel):
    id: int
    user_id: int
    date: date
    start_time: time
    end_time: time
    status: str
    created_at: datetime
    user: UserInfo

    class Config:
        from_attributes = True

class PublicBookingResponse(BaseModel):
    """Public response schema - no sensitive user information."""
    id: int
    booking_date: date
    start_time: time
    end_time: time

    class Config:
        from_attributes = True