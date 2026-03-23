from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.blocked_date import BlockedDate
from app.schemas.booking import BookingCreate, BookingResponse, PublicBookingResponse
from app.utils.dependencies import get_current_user, admin_required, get_current_organization
from app.models.organization import Organization
from datetime import datetime, time as dt_time, timedelta, date as dt_date
from typing import List
import pytz

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# Business hours constants
BUSINESS_START = dt_time(9, 0)  # 09:00 AM
BUSINESS_END = dt_time(21, 0)   # 09:00 PM


def expire_pending_bookings(db: Session):
    """
    Automatically mark expired pending bookings.
    
    Finds all pending bookings where the end datetime has passed
    and updates their status to 'expired'.
    """
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    current_date = now.date()
    current_time = now.time()
    
    expired_bookings = db.query(Booking).filter(
        and_(
            Booking.status == BookingStatus.pending,
            or_(
                Booking.date < current_date,
                and_(Booking.date == current_date, Booking.end_time < current_time)
            )
        )
    ).all()
    
    if expired_bookings:
        for booking in expired_bookings:
            booking.status = BookingStatus.expired
        db.commit()
    
    return len(expired_bookings)


def validate_business_hours(start_time: dt_time, end_time: dt_time) -> bool:
    """Validate that booking is within business hours."""
    return start_time >= BUSINESS_START and end_time <= BUSINESS_END


def check_overlap(db: Session, user_id: int, booking_date: dt_date,
                  start_time: dt_time, end_time: dt_time, exclude_booking_id: int = None, org_id: int = None) -> bool:
    """Check if booking overlaps with existing bookings within the same organization."""
    query = db.query(Booking).filter(
        and_(
            Booking.date == booking_date,
            Booking.status.in_([BookingStatus.pending, BookingStatus.approved]),
            Booking.start_time < end_time,
            Booking.end_time > start_time
        )
    )

    if org_id is not None:
        query = query.filter(Booking.organization_id == org_id)

    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)

    overlapping_booking = query.first()

    if overlapping_booking:
        print(f"⚠️  Overlap detected with booking ID {overlapping_booking.id}")

    return overlapping_booking is not None


@router.post("/", response_model=BookingResponse)
def create_booking(
    booking: BookingCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization)
):
    """Create a new booking scoped to the current organization."""

    # Check if date is blocked (scoped to org)
    blocked_date = db.query(BlockedDate).filter(
        BlockedDate.date == booking.date,
        BlockedDate.organization_id == current_org.id
    ).first()

    if blocked_date:
        reason_msg = f": {blocked_date.reason}" if blocked_date.reason else ""
        raise HTTPException(status_code=400, detail=f"All slots are unavailable for this date{reason_msg}")

    start_datetime = datetime.combine(booking.date, booking.start_time)
    end_datetime = start_datetime + timedelta(minutes=booking.duration_minutes)
    end_time = end_datetime.time()

    if end_datetime.date() > booking.date:
        raise HTTPException(status_code=400, detail="Booking duration extends beyond the selected date")

    if not validate_business_hours(booking.start_time, end_time):
        raise HTTPException(
            status_code=400,
            detail=f"Booking must be within business hours ({BUSINESS_START.strftime('%I:%M %p')} - {BUSINESS_END.strftime('%I:%M %p')}). Your booking would end at {end_time.strftime('%I:%M %p')}."
        )

    if check_overlap(db, current_user.id, booking.date, booking.start_time, end_time, org_id=current_org.id):
        conflicting = db.query(Booking).filter(
            and_(
                Booking.date == booking.date,
                Booking.organization_id == current_org.id,
                Booking.status.in_([BookingStatus.pending, BookingStatus.approved]),
                Booking.start_time < end_time,
                Booking.end_time > booking.start_time
            )
        ).first()

        if conflicting:
            raise HTTPException(
                status_code=400,
                detail=f"Time slot unavailable. Conflicts with existing booking from {conflicting.start_time.strftime('%I:%M %p')} to {conflicting.end_time.strftime('%I:%M %p')}."
            )
        raise HTTPException(status_code=400, detail="This time slot is not available")

    new_booking = Booking(
        user_id=current_user.id,
        organization_id=current_org.id,
        date=booking.date,
        start_time=booking.start_time,
        end_time=end_time,
        description=booking.description,
        company_name=booking.company_name,
        hr_name=booking.hr_name,
        mobile_number=booking.mobile_number,
        email_id=booking.email_id,
        status=BookingStatus.pending,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    db_booking = db.query(Booking).options(
        joinedload(Booking.user)
    ).filter(Booking.id == new_booking.id).first()

    return db_booking


@router.get("/my-bookings", response_model=list[BookingResponse])
def my_bookings(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization)
):
    """Get current user's bookings scoped to their organization."""
    expire_pending_bookings(db)

    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    two_days_ago = now - timedelta(days=2)
    cutoff_date = two_days_ago.date()
    cutoff_time = two_days_ago.time()

    return db.query(Booking).options(
        joinedload(Booking.user)
    ).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.organization_id == current_org.id,
            or_(
                Booking.date > cutoff_date,
                and_(Booking.date == cutoff_date, Booking.end_time >= cutoff_time)
            )
        )
    ).all()


@router.get("/", response_model=list[BookingResponse])
def get_all_bookings(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required),
    current_org: Organization = Depends(get_current_organization)
):
    """Get all bookings for the current organization (admin only)."""
    expire_pending_bookings(db)

    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    two_days_ago = now - timedelta(days=2)
    cutoff_date = two_days_ago.date()
    cutoff_time = two_days_ago.time()

    return db.query(Booking).options(
        joinedload(Booking.user)
    ).filter(
        and_(
            Booking.organization_id == current_org.id,
            or_(
                Booking.date > cutoff_date,
                and_(Booking.date == cutoff_date, Booking.end_time >= cutoff_time)
            )
        )
    ).all()


@router.put("/{booking_id}/approve")
def approve_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    """Approve a pending booking (admin only)."""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == BookingStatus.approved:
        raise HTTPException(status_code=400, detail="Booking already approved")
    
    if booking.status == BookingStatus.rejected:
        raise HTTPException(status_code=400, detail="Cannot approve rejected booking")
    
    if booking.status == BookingStatus.expired:
        raise HTTPException(status_code=400, detail="Cannot approve expired booking")
    
    booking.status = BookingStatus.approved
    db.commit()
    
    return {"message": "Booking approved"}


@router.put("/{booking_id}/reject")
def reject_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    """Reject a pending booking (admin only)."""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == BookingStatus.approved:
        raise HTTPException(status_code=400, detail="Cannot reject approved booking")
    
    if booking.status == BookingStatus.rejected:
        raise HTTPException(status_code=400, detail="Booking already rejected")
    
    booking.status = BookingStatus.rejected
    db.commit()
    
    return {"message": "Booking rejected"}


@router.get("/active")
def get_active_bookings(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization)
):
    """Get only active approved bookings for the current user in their organization."""
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    current_date = now.date()
    current_time = now.time()

    active_bookings = db.query(Booking).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.organization_id == current_org.id,
            Booking.status == BookingStatus.approved,
            or_(
                Booking.date > current_date,
                and_(Booking.date == current_date, Booking.end_time >= current_time)
            )
        )
    ).options(joinedload(Booking.user)).all()

    return {
        "active_count": len(active_bookings),
        "active_bookings": active_bookings
    }


@router.get("/available-times")
def get_available_times(
    date: dt_date,
    duration_minutes: int,
    request: Request,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get available time slots for a given date and duration (scoped to organization)."""
    allowed_durations = [30, 60, 90, 120]
    if duration_minutes not in allowed_durations:
        raise HTTPException(status_code=400, detail=f"Duration must be one of {allowed_durations} minutes")

    if date < dt_date.today():
        return {"date": date, "duration_minutes": duration_minutes, "available_slots": []}

    existing_bookings = db.query(Booking).filter(
        and_(
            Booking.date == date,
            Booking.organization_id == current_org.id,
            Booking.status.in_([BookingStatus.pending, BookingStatus.approved])
        )
    ).order_by(Booking.start_time).all()

    available_slots = []
    current_time = datetime.combine(date, BUSINESS_START)
    end_of_day = datetime.combine(date, BUSINESS_END)

    while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
        slot_start = current_time.time()
        slot_end = (current_time + timedelta(minutes=duration_minutes)).time()

        is_available = True
        for booking in existing_bookings:
            if slot_start < booking.end_time and slot_end > booking.start_time:
                is_available = False
                break

        if is_available:
            available_slots.append({
                "start_time": slot_start.strftime("%H:%M"),
                "end_time": slot_end.strftime("%H:%M")
            })

        current_time += timedelta(minutes=15)

    return {"date": date, "duration_minutes": duration_minutes, "available_slots": available_slots}


@router.get("/approved-public")
def get_approved_bookings_public(
    request: Request,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get all approved bookings for the current organization (Public endpoint).
    No authentication required.
    """
    
    bookings = (
        db.query(Booking)
        .filter(
            Booking.status == BookingStatus.approved,
            Booking.organization_id == current_org.id
        )
        .order_by(Booking.date, Booking.start_time)
        .all()
    )
    
    result = [
        {
            "id": booking.id,
            "booking_date": booking.date.isoformat() if booking.date else None,
            "start_time": booking.start_time.isoformat() if booking.start_time else None,
            "end_time": booking.end_time.isoformat() if booking.end_time else None
        }
        for booking in bookings
    ]
    
    return result


@router.get("/approved-public-debug")
def get_approved_bookings_debug(
    db: Session = Depends(get_db)
):
    """Debug endpoint to check what's in the database."""
    
    all_bookings = db.query(Booking).all()
    approved_bookings = db.query(Booking).filter(Booking.status == BookingStatus.approved).all()
    
    return {
        "total_bookings": len(all_bookings),
        "approved_bookings": len(approved_bookings),
        "approved_list": [
            {
                "id": b.id,
                "booking_date": str(b.date),
                "start_time": str(b.start_time),
                "end_time": str(b.end_time),
                "status": b.status.value
            }
            for b in approved_bookings
        ]
    }


@router.patch("/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization)
):
    """Cancel a booking (User can cancel their own, Admin can cancel any)."""
    
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.organization_id == current_org.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Authorization check
    is_admin = current_user.role.value == "admin"
    is_owner = booking.user_id == current_user.id
    
    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to cancel this booking"
        )
    
    # Validate booking can be cancelled
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    if booking.status == BookingStatus.rejected:
        raise HTTPException(status_code=400, detail="Cannot cancel rejected booking")
    
    # Check if booking is in the past
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    booking_datetime = datetime.combine(booking.date, booking.end_time)
    booking_datetime = pytz.timezone('Asia/Kolkata').localize(booking_datetime)
    
    if booking_datetime < now:
        raise HTTPException(status_code=400, detail="Cannot cancel past bookings")
    
    # Cancel the booking
    booking.status = BookingStatus.cancelled
    booking.cancelled_at = datetime.now(pytz.timezone('Asia/Kolkata'))
    booking.cancelled_by = current_user.id
    
    db.commit()
    db.refresh(booking)
    
    return {
        "message": "Booking cancelled successfully",
        "booking_id": booking.id,
        "cancelled_at": booking.cancelled_at,
        "cancelled_by": current_user.name
    }
