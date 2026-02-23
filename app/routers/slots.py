from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.slot import Slot
from app.schemas.slot import SlotCreate, SlotResponse
from app.utils.dependencies import admin_required, get_current_user
from datetime import datetime
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
    """Get all slots for admin (includes past slots)"""
    today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    
    # Auto-deactivate past slots
    db.query(Slot).filter(
        Slot.date < today,
        Slot.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    return db.query(Slot).order_by(Slot.date.desc(), Slot.start_time).all()

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