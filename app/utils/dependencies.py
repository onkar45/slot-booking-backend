from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
DEFAULT_SUBDOMAIN = os.getenv("DEFAULT_SUBDOMAIN", "")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _extract_org_slug(request: Request) -> str | None:
    """
    Extract org slug from request using hybrid detection:
    - Dev/local: X-Org-Slug header (highest priority)
    - Production: subdomain from Host header (e.g. tcs.cernsystem.com → "tcs")
    - Localhost/IP fallback: DEFAULT_SUBDOMAIN from env
    Returns None if no slug can be determined.
    """
    # 1. X-Org-Slug header takes priority (dev / localhost explicit override)
    slug = request.headers.get("x-org-slug")
    if slug:
        return slug.strip().lower()

    # 2. Extract subdomain from Host header (production)
    host = request.headers.get("host", "").split(":")[0]  # strip port
    parts = host.split(".")
    if len(parts) > 2:
        candidate = parts[0].strip().lower()
        if candidate and candidate != "www":
            return candidate

    # 3. Localhost / direct IP fallback — use DEFAULT_SUBDOMAIN from env
    if DEFAULT_SUBDOMAIN:
        return DEFAULT_SUBDOMAIN

    return None


def get_current_organization(request: Request, db: Session = Depends(get_db)) -> Organization:
    """
    Hybrid multi-tenant org detection.
    Priority:
    1. X-Org-Slug header (dev / localhost)
    2. Subdomain from Host header (production, e.g. tcs.cernsystem.com)
    Returns 400 if no slug found, 404 if org not found or inactive.
    """
    slug = _extract_org_slug(request)

    if not slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization could not be determined. Provide X-Org-Slug header or use a subdomain."
        )

    org = db.query(Organization).filter(
        Organization.subdomain == slug,
        Organization.is_active == True
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{slug}' not found or inactive."
        )

    return org


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive account")

    return user


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role.value not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def super_admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "super_admin":
        raise HTTPException(status_code=403, detail="Super Admin access required")
    return current_user
