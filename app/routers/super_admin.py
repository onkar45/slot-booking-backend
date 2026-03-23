from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.login_activity import LoginActivity
from app.models.organization import Organization
from app.schemas.super_admin import DashboardStats, CompanyAnalytics, LoginActivityResponse, SuperAdminBookingResponse, CreateOrgAdmin, OrgAdminResponse
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationWithAdminResponse
from app.utils.dependencies import super_admin_required
from app.utils.hash import hash_password
from app.models.user import UserRole
import pytz
from datetime import datetime

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

@router.get("/login-activity")
def get_login_activity(
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    activities = (
        db.query(LoginActivity)
        .order_by(LoginActivity.login_time.desc())
        .all()
    )

    result = []
    for activity in activities:
        user = db.query(User).filter(User.id == activity.user_id).first()
        org = db.query(Organization).filter(Organization.id == user.organization_id).first() if user else None
        result.append({
            "id": activity.id,
            "user_id": activity.user_id,
            "ip_address": activity.ip_address,
            "user_agent": activity.user_agent,
            "login_time": activity.login_time,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            } if user else None,
            "organization": {
                "id": org.id,
                "name": org.name,
                "slug": org.subdomain,
            } if org else None,
        })
    return result


# ==================== ORGANIZATION MANAGEMENT ====================

@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """Create a new organization (Super Admin only)."""
    existing = db.query(Organization).filter(
        Organization.subdomain == org_data.subdomain
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Subdomain '{org_data.subdomain}' is already taken"
        )

    org = Organization(
        name=org_data.name,
        subdomain=org_data.subdomain
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/organizations", response_model=List[OrganizationWithAdminResponse])
def list_organizations(
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """List all organizations with their admin info (Super Admin only)."""
    orgs = db.query(Organization).order_by(Organization.created_at.desc()).all()
    result = []
    for org in orgs:
        admin = db.query(User).filter(
            User.organization_id == org.id,
            User.role == UserRole.admin
        ).first()
        result.append(OrganizationWithAdminResponse(
            id=org.id,
            name=org.name,
            subdomain=org.subdomain,
            is_active=org.is_active,
            created_at=org.created_at,
            admin_email=admin.email if admin else None,
            admin_name=admin.name if admin else None,
        ))
    return result


@router.post("/organizations/{org_id}/admin", response_model=OrgAdminResponse, status_code=status.HTTP_201_CREATED)
def create_org_admin(
    org_id: int,
    admin_data: CreateOrgAdmin,
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """Create an admin user for a specific organization (Super Admin only)."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not org.is_active:
        raise HTTPException(status_code=400, detail="Organization is inactive")

    if db.query(User).filter(User.email == admin_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_admin = User(
        name=admin_data.name,
        email=admin_data.email,
        password=hash_password(admin_data.password),
        role=UserRole.admin,
        organization_id=org_id,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


@router.put("/organizations/{org_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """Deactivate an organization (Super Admin only)."""
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not org.is_active:
        raise HTTPException(status_code=400, detail="Organization is already inactive")

    org.is_active = False
    db.commit()

    return {"message": f"Organization '{org.name}' deactivated"}


@router.put("/organizations/{org_id}/activate", status_code=status.HTTP_200_OK)
def activate_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(super_admin_required)
):
    """Activate an organization (Super Admin only)."""
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if org.is_active:
        raise HTTPException(status_code=400, detail="Organization is already active")

    org.is_active = True
    db.commit()

    return {"message": f"Organization '{org.name}' activated"}
