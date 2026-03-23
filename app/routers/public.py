from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.blocked_date import BlockedDate
from app.models.organization import Organization
from app.utils.dependencies import get_current_organization

router = APIRouter(tags=["Public"])


@router.get("/blocked-dates-public")
def get_blocked_dates_public(
    request: Request,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get all blocked dates for the current organization (Public - no auth required).
    Used by the calendar to show unavailable dates.
    """
    blocked_dates = db.query(BlockedDate).filter(
        BlockedDate.organization_id == current_org.id
    ).order_by(BlockedDate.date).all()

    return [
        {
            "id": blocked.id,
            "date": blocked.date,
            "reason": blocked.reason
        }
        for blocked in blocked_dates
    ]
