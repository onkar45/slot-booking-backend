from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, Date, Time, Text, String
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
    cancelled = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dynamic time-based fields
    date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    description = Column(Text, nullable=True)
    
    # New fields for company/HR information
    company_name = Column(String(255), nullable=True)
    hr_name = Column(String(255), nullable=True)
    mobile_number = Column(String(20), nullable=True)
    email_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    # Cancellation tracking fields
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by])