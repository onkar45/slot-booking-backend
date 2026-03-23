from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.login_activity import LoginActivity
from app.models.organization import Organization
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.utils.dependencies import get_current_organization
from datetime import datetime
from user_agents import parse
import pytz
import os


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    Handles cases where app is behind a proxy/load balancer.
    """
    # Check X-Forwarded-For header (set by proxies/load balancers)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header (alternative proxy header)
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fallback to direct client host
    if request.client:
        return request.client.host
    
    return "Unknown"


def get_browser_info(request: Request) -> str:
    """
    Extract and parse browser information from User-Agent header.
    Returns a clean browser name instead of full user-agent string.
    """
    user_agent = request.headers.get("user-agent", "Unknown")
    
    if user_agent == "Unknown":
        return "Unknown Browser"
    
    try:
        # Parse user agent string
        ua = parse(user_agent)
        
        # Get browser family and version
        browser = ua.browser.family
        version = ua.browser.version_string
        
        # Get OS info
        os = ua.os.family
        
        # Return formatted string
        if version:
            return f"{browser} {version} on {os}"
        else:
            return f"{browser} on {os}"
    except Exception:
        # If parsing fails, return the raw user-agent
        return user_agent[:255]  # Truncate to fit database column


# Public registration disabled - use /admin/users endpoint (admin only)
# @router.post("/register", response_model=UserResponse)
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     raise HTTPException(
#         status_code=403,
#         detail="Public registration is disabled. Contact administrator."
#     )

@router.post("/login")
def login(
    user: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not db_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been deactivated. Please contact admin."
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Validate user belongs to this organization
    # Super admins can log in from any org/subdomain
    if db_user.role.value != "super_admin":
        if db_user.organization_id != current_org.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this organization."
            )

    # Capture IP address and browser info
    ip_address = get_client_ip(request)
    browser_info = get_browser_info(request)

    # Create access token
    token = create_access_token(
        data={
            "user_id": db_user.id,
            "role": db_user.role.value
        }
    )

    # Record login activity with captured information
    login_activity = LoginActivity(
        user_id=db_user.id,
        ip_address=ip_address,
        user_agent=browser_info
    )
    db.add(login_activity)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role.value
    }

@router.post("/token")
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login for Swagger UI authorization. No org check required."""
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Check if account is active before password verification
    if not db_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been deactivated. Please contact admin."
        )

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Capture IP address and browser info
    ip_address = get_client_ip(request) if request else "Unknown"
    browser_info = get_browser_info(request) if request else "Unknown Browser"

    # Create access token
    token = create_access_token(
        data={
            "user_id": db_user.id,
            "role": db_user.role.value
        }
    )

    # Record login activity with captured information
    login_activity = LoginActivity(
        user_id=db_user.id,
        ip_address=ip_address,
        user_agent=browser_info
    )
    db.add(login_activity)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer"
    }
