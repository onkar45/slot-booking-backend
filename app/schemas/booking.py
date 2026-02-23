from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional

class SlotInfo(BaseModel):
    id: int
    date: date
    start_time: time
    end_time: time
    is_active: bool

    class Config:
        from_attributes = True

class UserInfo(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    slot_id: int

class BookingResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    status: str
    created_at: datetime
    slot: SlotInfo
    user: UserInfo

    class Config:
        from_attributes = True