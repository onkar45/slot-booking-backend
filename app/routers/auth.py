from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_access_token
from datetime import datetime
import pytz


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role
    try:
        user_role = UserRole(user.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be 'user' or 'admin'")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user_role,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(
        data={
            "user_id": db_user.id,
            "role": db_user.role.value
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role.value
    }

@router.post("/token")
def login_oauth(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token login for Swagger UI authorization"""
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(
        data={
            "user_id": db_user.id,
            "role": db_user.role.value
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
