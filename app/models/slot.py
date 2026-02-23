from sqlalchemy import Column, Integer, Date, Time, Boolean, DateTime
from app.database import Base
from datetime import datetime
import pytz

class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable = False)
    start_time = Column(Time, nullable = False)
    end_time = Column(Time, nullable= False)
    is_active =  Column(Boolean, default = True)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))