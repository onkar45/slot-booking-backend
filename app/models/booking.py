from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime
import pytz

class BookingStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    slot_id = Column(Integer, ForeignKey("slots.id"))

    status = Column(Enum(BookingStatus), default=BookingStatus.pending)

    created_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))

    user = relationship("User")
    slot = relationship("Slot")