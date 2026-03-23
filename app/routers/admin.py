from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.blocked_date import BlockedDate
from app.models.login_activity import LoginActivity
from app.models.organization import Organization
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserResponse
from app.schemas.blocked_date import BlockedDateCreate, BlockedDateResponse, BlockedDateWithCreator
from app.utils.hash import hash_password
from app.utils.dependencies import admin_required, get_current_organization
from datetime import datetime, timezone, date as dt_date
import pytz


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required),
    current_org: Organization = Depends(get_current_organization)
):
    """Get all users in the current organization (Admin only)."""
    users = db.query(User).filter(User.organization_id == current_org.id).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: AdminUserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required),
    current_org: Organization = Depends(get_current_organization)
):
    """Create a new user account scoped to the current organization (Admin only)."""
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if name already exists
    existing_name = db.query(User).filter(User.name == user_data.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already taken"
        )
    
    # Validate role - prevent admin creation
    if user_data.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create admin users through this endpoint"
        )
    
    # Validate role enum
    try:
        user_role = UserRole(user_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'user'"
        )
    
    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_role,
        organization_id=current_org.id,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Update user account (Admin only).
    
    - Requires admin authentication
    - Admin cannot edit their own role
    - Admin cannot modify other admins
    - Can update: name, email, is_active
    - Name and email must be unique
    - Password changes not allowed here
    """
    
    # Fetch user to update
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from modifying other admins
    if user.role.value == "admin" and user.id != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other admin accounts"
        )
    
    # Prevent admin from editing their own role (if role field existed in update)
    if user.id == current_admin.id and user_data.is_active is not None:
        if not user_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deactivate your own account"
            )
    
    # Check name uniqueness if being updated
    if user_data.name is not None and user_data.name != user.name:
        existing_name = db.query(User).filter(
            User.name == user_data.name,
            User.id != user_id
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name already taken"
            )
        user.name = user_data.name
    
    # Check email uniqueness if being updated
    if user_data.email is not None and user_data.email != user.email:
        existing_email = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email
    
    # Update is_active if provided
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/users/{user_id}/activate", response_model=UserResponse)
def toggle_user_activation(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Toggle user active status (Admin only).
    
    - Requires admin authentication
    - Activates or deactivates a user account
    - Cannot deactivate self
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate your own account"
        )
    
    # Toggle is_active status
    user.is_active = not user.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/users/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Activate a user account (Admin only).
    
    - Requires admin authentication
    - Sets user account to active
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Deactivate a user account (Admin only).
    
    - Requires admin authentication
    - Sets user account to inactive
    - Cannot deactivate self
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Delete a user (Admin only).
    
    - Requires admin authentication
    - Permanently deletes a user account
    - Cannot delete self
    - Cannot delete other admins
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )
    
    # Prevent admin from deleting other admins
    if user.role.value == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin accounts"
        )
    
    db.delete(user)
    db.commit()
    
    return None


# ==================== BLOCKED DATES ENDPOINTS ====================

@router.post("/block-date", response_model=BlockedDateResponse, status_code=status.HTTP_201_CREATED)
def block_date(
    blocked_date: BlockedDateCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required),
    current_org: Organization = Depends(get_current_organization)
):
    """Block a date for the current organization (Admin only)."""
    
    # Check if date is already blocked for this org
    existing_blocked = db.query(BlockedDate).filter(
        BlockedDate.date == blocked_date.date,
        BlockedDate.organization_id == current_org.id
    ).first()
    
    if existing_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Date {blocked_date.date} is already blocked"
        )
    
    new_blocked_date = BlockedDate(
        date=blocked_date.date,
        reason=blocked_date.reason,
        created_by=current_admin.id,
        organization_id=current_org.id,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )
    
    db.add(new_blocked_date)
    db.commit()
    db.refresh(new_blocked_date)
    
    return new_blocked_date


@router.get("/blocked-dates", response_model=list[BlockedDateWithCreator])
def get_blocked_dates(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required),
    current_org: Organization = Depends(get_current_organization)
):
    """Get all blocked dates for the current organization (Admin only)."""
    
    blocked_dates = db.query(BlockedDate).options(
        joinedload(BlockedDate.creator)
    ).filter(
        BlockedDate.organization_id == current_org.id
    ).order_by(BlockedDate.date).all()
    
    # Format response with creator info
    result = []
    for blocked in blocked_dates:
        result.append({
            "id": blocked.id,
            "date": blocked.date,
            "reason": blocked.reason,
            "created_by": blocked.created_by,
            "created_at": blocked.created_at,
            "creator": {
                "id": blocked.creator.id,
                "name": blocked.creator.name,
                "email": blocked.creator.email
            }
        })
    
    return result


@router.delete("/unblock-date/{blocked_date_id}", status_code=status.HTTP_200_OK)
def unblock_date(
    blocked_date_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Remove a blocked date (Admin only).
    
    - Requires admin authentication
    - Allows bookings to be made on that date again
    """
    
    blocked_date = db.query(BlockedDate).filter(
        BlockedDate.id == blocked_date_id
    ).first()
    
    if not blocked_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked date not found"
        )
    
    db.delete(blocked_date)
    db.commit()
    
    return {
        "message": f"Date {blocked_date.date} has been unblocked",
        "date": blocked_date.date
    }


@router.get("/blocked-dates/check/{date}")
def check_date_blocked(
    date: dt_date,
    db: Session = Depends(get_db)
):
    """
    Check if a specific date is blocked (Public endpoint).
    
    - No authentication required
    - Returns whether the date is blocked and reason
    """
    
    blocked = db.query(BlockedDate).filter(BlockedDate.date == date).first()
    
    if blocked:
        return {
            "is_blocked": True,
            "date": date,
            "reason": blocked.reason
        }
    
    return {
        "is_blocked": False,
        "date": date
    }


# ==================== LOGIN ACTIVITY ENDPOINTS ====================

@router.get("/login-activity")
def get_login_activity(
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Get all login activities with user details (Admin only).
    
    - Requires admin authentication
    - Returns login history with user information
    - Sorted by login time (most recent first)
    """
    
    # Fetch all login activities with user relationship
    activities = db.query(LoginActivity).options(
        joinedload(LoginActivity.user)
    ).order_by(LoginActivity.login_time.desc()).all()
    
    # Format response with user details
    result = []
    for activity in activities:
        user_data = None
        if activity.user:
            user_data = {
                "id": activity.user.id,
                "name": activity.user.name,
                "email": activity.user.email,
                "username": getattr(activity.user, 'username', None)
            }
        
        result.append({
            "id": activity.id,
            "user_id": activity.user_id,
            "ip_address": activity.ip_address,
            "user_agent": activity.user_agent,
            "login_time": activity.login_time,
            "user": user_data
        })
    
    return result


@router.get("/login-activity/{user_id}")
def get_user_login_activity(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_required)
):
    """
    Get login activities for a specific user (Admin only).
    
    - Requires admin authentication
    - Returns login history for specified user
    - Sorted by login time (most recent first)
    """
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Fetch user's login activities
    activities = db.query(LoginActivity).filter(
        LoginActivity.user_id == user_id
    ).order_by(LoginActivity.login_time.desc()).all()
    
    # Format response
    result = []
    for activity in activities:
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
                "username": getattr(user, 'username', None)
            }
        })
    
    return result

