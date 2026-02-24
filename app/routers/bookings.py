from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.slot import Slot
from app.schemas.booking import BookingCreate, BookingResponse
from app.utils.dependencies import get_current_user, admin_required
from datetime import datetime
import pytz

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=BookingResponse)
def book_slot(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Check if slot exists
    slot = db.query(Slot).filter(Slot.id == booking.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    # Check if slot is active
    if not slot.is_active:
        raise HTTPException(status_code=400, detail="Slot is not active")

    # Check if slot date is in the past
    if slot.date < datetime.now(pytz.timezone('Asia/Kolkata')).date():
        raise HTTPException(status_code=400, detail="Cannot book past slots")

    # Check if user already has a pending/approved booking for this slot
    existing_user_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.slot_id == booking.slot_id,
        Booking.status.in_([BookingStatus.pending, BookingStatus.approved])
    ).first()

    if existing_user_booking:
        raise HTTPException(status_code=400, detail="You already have a booking for this slot")

    # Check if slot already approved
    approved_booking = db.query(Booking).filter(
        Booking.slot_id == booking.slot_id,
        Booking.status == BookingStatus.approved
    ).first()

    if approved_booking:
        raise HTTPException(status_code=400, detail="Slot already booked")

    new_booking = Booking(
        user_id=current_user.id,
        slot_id=booking.slot_id,
        status=BookingStatus.pending,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # Load relationships
    db_booking = db.query(Booking).options(
        joinedload(Booking.slot),
        joinedload(Booking.user)
    ).filter(Booking.id == new_booking.id).first()

    return db_booking

@router.get("/my-bookings", response_model=list[BookingResponse])
def my_bookings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Booking).options(
        joinedload(Booking.slot),
        joinedload(Booking.user)
    ).filter(
        Booking.user_id == current_user.id
    ).all()

@router.get("/", response_model=list[BookingResponse])
def get_all_bookings(
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    return db.query(Booking).options(
        joinedload(Booking.slot),
        joinedload(Booking.user)
    ).all()

@router.put("/{booking_id}/approve")
def approve_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):

    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == BookingStatus.approved:
        raise HTTPException(status_code=400, detail="Booking already approved")

    if booking.status == BookingStatus.rejected:
        raise HTTPException(status_code=400, detail="Cannot approve rejected booking")

    # Check if slot still exists and is active
    slot = db.query(Slot).filter(Slot.id == booking.slot_id).first()
    if not slot or not slot.is_active:
        raise HTTPException(status_code=400, detail="Slot is not available")

    # Double safety check
    existing_approved = db.query(Booking).filter(
        Booking.slot_id == booking.slot_id,
        Booking.status == BookingStatus.approved,
        Booking.id != booking_id
    ).first()

    if existing_approved:
        raise HTTPException(status_code=400, detail="Slot already approved for another user")

    booking.status = BookingStatus.approved
    db.commit()

    return {"message": "Booking approved"}

@router.put("/{booking_id}/reject")
def reject_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):

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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get only active (approved and not expired) bookings for the current user"""
    from sqlalchemy import and_, func
    from datetime import datetime, time as dt_time
    
    # Get current datetime in Asia/Kolkata timezone
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    current_date = now.date()
    current_time = now.time()
    
    # Query active bookings with database-level filtering
    active_bookings = db.query(Booking).join(Slot).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.status == BookingStatus.approved,
            # Filter out past slots: either future date OR (today AND end_time >= current_time)
            (Slot.date > current_date) | 
            (and_(Slot.date == current_date, Slot.end_time >= current_time))
        )
    ).options(
        joinedload(Booking.slot),
        joinedload(Booking.user)
    ).all()
    
    return {
        "active_count": len(active_bookings),
        "active_bookings": active_bookings
    }
