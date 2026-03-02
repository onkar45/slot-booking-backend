from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, Date, Time, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime
import pytz

class BookingStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"
    cancelled = "cancelled"  # New status

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dynamic time-based fields (nullable=True to match migration)
    date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    # Cancellation tracking fields
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by])