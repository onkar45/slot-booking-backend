from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.slot import Slot
from app.schemas.slot import SlotCreate, SlotResponse
from app.utils.dependencies import admin_required, get_current_user
from datetime import datetime, timedelta
import pytz


router = APIRouter(prefix = "/slots", tags=["slots"])

@router.post("/", response_model=SlotResponse)
def create_slot(
    slot: SlotCreate,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    
    # Check for overlapping slots on the same date
    overlapping_slot = db.query(Slot).filter(
        Slot.date == slot.date,
        Slot.start_time < slot.end_time,
        Slot.end_time > slot.start_time
    ).first()

    if overlapping_slot:
        raise HTTPException(
            status_code=400, 
            detail=f"Slot overlaps with existing slot: {overlapping_slot.start_time} - {overlapping_slot.end_time}"
        )

    new_slot = Slot(
        date=slot.date,
        start_time=slot.start_time,
        end_time=slot.end_time,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return new_slot

@router.get("/", response_model=list[SlotResponse])
def get_all_slots(
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    """Get all slots for admin (excludes slots older than 2 days)"""
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    today = now.date()
    
    # Calculate cutoff datetime (2 days ago)
    two_days_ago = now - timedelta(days=2)
    cutoff_date = two_days_ago.date()
    cutoff_time = two_days_ago.time()
    
    # Auto-deactivate past slots
    db.query(Slot).filter(
        Slot.date < today,
        Slot.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    # Fetch all slots excluding those older than 2 days
    slots = db.query(Slot).filter(
        # Include slots where slot end datetime >= 2 days ago
        (Slot.date > cutoff_date) | 
        ((Slot.date == cutoff_date) & (Slot.end_time >= cutoff_time))
    ).order_by(Slot.date.desc(), Slot.start_time).all()
    
    return slots

@router.get("/available", response_model=list[SlotResponse])
def get_available_slots(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all active slots that are not in the past"""
    today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    
    # Auto-deactivate past slots
    db.query(Slot).filter(
        Slot.date < today,
        Slot.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    # Return only future active slots
    return db.query(Slot).filter(
        Slot.is_active == True,
        Slot.date >= today
    ).order_by(Slot.date, Slot.start_time).all()

@router.put("/{slot_id}/deactivate")
def deactivate_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    slot = db.query(Slot).filter(Slot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    slot.is_active = False
    db.commit()

    return {"message": "Slot deactivated"}

@router.put("/{slot_id}/activate")
def activate_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    slot = db.query(Slot).filter(Slot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    # Prevent activating past slots
    today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    if slot.date < today:
        raise HTTPException(status_code=400, detail="Cannot activate past slots")

    slot.is_active = True
    db.commit()

    return {"message": "Slot activated"}

@router.get("/public", response_model=list)
def get_public_slots(db: Session = Depends(get_db)):
    """Public endpoint - no authentication required. Shows all slots with booking status (excludes slots older than 2 days)."""
    from app.models.booking import Booking, BookingStatus
    
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    today = now.date()
    
    # Calculate cutoff datetime (2 days ago)
    two_days_ago = now - timedelta(days=2)
    cutoff_date = two_days_ago.date()
    cutoff_time = two_days_ago.time()
    
    # Auto-deactivate past slots
    db.query(Slot).filter(
        Slot.date < today,
        Slot.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    # Get all slots excluding those older than 2 days
    slots = db.query(Slot).filter(
        # Include slots where slot end datetime >= 2 days ago
        (Slot.date > cutoff_date) | 
        ((Slot.date == cutoff_date) & (Slot.end_time >= cutoff_time))
    ).order_by(Slot.date, Slot.start_time).all()
    
    result = []
    for slot in slots:
        # Check if slot has approved booking
        approved_booking = db.query(Booking).filter(
            Booking.slot_id == slot.id,
            Booking.status == BookingStatus.approved
        ).first()
        
        is_booked = approved_booking is not None
        
        # Determine status
        if not slot.is_active:
            status = "inactive"
        elif is_booked:
            status = "booked"
        else:
            status = "available"
        
        result.append({
            "id": slot.id,
            "date": slot.date,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "is_active": slot.is_active,
            "is_booked": is_booked,
            "status": status
        })
    
    return result
