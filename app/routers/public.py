from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.blocked_date import BlockedDate
from datetime import date as dt_date

router = APIRouter(tags=["Public"])


@router.get("/blocked-dates-public")
def get_blocked_dates_public(db: Session = Depends(get_db)):
    """
    Get all blocked dates (Public endpoint - no authentication required).
    
    Returns list of dates that are blocked for booking.
    Used by the calendar to show unavailable dates.
    """
    
    blocked_dates = db.query(BlockedDate).order_by(BlockedDate.date).all()
    
    # Return simple list of dates
    return [
        {
            "id": blocked.id,
            "date": blocked.date,
            "reason": blocked.reason
        }
        for blocked in blocked_dates
    ]
