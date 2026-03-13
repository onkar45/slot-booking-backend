from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.login_activity import LoginActivity
from app.schemas.super_admin import DashboardStats, CompanyAnalytics, LoginActivityResponse, SuperAdminBookingResponse
from app.utils.dependencies import super_admin_required

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """
    Get system dashboard statistics (Super Admin only).
    """
    total_users = db.query(User).count()
    total_bookings = db.query(Booking).count()
    approved_bookings = db.query(Booking).filter(Booking.status == BookingStatus.approved).count()
    pending_bookings = db.query(Booking).filter(Booking.status == BookingStatus.pending).count()

    return DashboardStats(
        total_users=total_users,
        total_bookings=total_bookings,
        approved_bookings=approved_bookings,
        pending_bookings=pending_bookings
    )

@router.get("/user-bookings")
def get_user_bookings(
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """
    View candidate booking history (Super Admin only).
    """
    from sqlalchemy.orm import joinedload
    bookings = db.query(Booking).options(joinedload(Booking.user)).all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "user_id": b.user_id,
            "date": b.date.isoformat() if b.date else None,
            "start_time": b.start_time.isoformat() if b.start_time else None,
            "end_time": b.end_time.isoformat() if b.end_time else None,
            "status": b.status.value if b.status else None,
            "description": b.description,
            "company_name": b.company_name,
            "hr_name": b.hr_name,
            "mobile_number": b.mobile_number,
            "email_id": b.email_id,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "user": {
                "id": b.user.id,
                "name": b.user.name,
                "email": b.user.email,
            } if b.user else None,
        })
    return result

@router.get("/company-analytics", response_model=List[CompanyAnalytics])
def get_company_analytics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """
    View company analytics (Super Admin only).
    """
    companies = db.query(Booking.company_name).filter(Booking.company_name != None).distinct().all()
    analytics = []
    
    for (company,) in companies:
        total = db.query(Booking).filter(Booking.company_name == company).count()
        approved = db.query(Booking).filter(and_(Booking.company_name == company, Booking.status == BookingStatus.approved)).count()
        pending = db.query(Booking).filter(and_(Booking.company_name == company, Booking.status == BookingStatus.pending)).count()
        
        analytics.append(CompanyAnalytics(
            company_name=company,
            total_bookings=total,
            approved_bookings=approved,
            pending_bookings=pending
        ))
    
    return analytics

@router.delete("/bookings/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_approved_booking(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """
    Delete an approved booking (Super Admin only).
    """
    booking = db.query(Booking).filter(Booking.id == id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.status != BookingStatus.approved:
        raise HTTPException(status_code=400, detail="Can only delete approved bookings")
        
    db.delete(booking)
    db.commit()
    return None

@router.put("/free-slot/{id}")
def free_slot(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """
    Free a slot if interview is rescheduled (Super Admin only).
    This changes the status to cancelled.
    """
    booking = db.query(Booking).filter(Booking.id == id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.status in [BookingStatus.cancelled, BookingStatus.rejected]:
        raise HTTPException(status_code=400, detail="Booking is already cancelled or rejected")
        
    booking.status = BookingStatus.cancelled
    db.commit()
    
    return {"message": "Slot freed successfully", "booking_id": id}

@router.get("/login-activity", response_model=List[LoginActivityResponse])
def get_login_activity(
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):

    activities = (
        db.query(LoginActivity)
        .options(joinedload(LoginActivity.user))
        .order_by(LoginActivity.login_time.desc())
        .all()
    )

    return activities
