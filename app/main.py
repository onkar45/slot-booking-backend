from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.routers import auth, bookings, admin, public, super_admin
from app.models import user, booking, blocked_date, login_activity, organization
from app.models.organization import Organization
from app.utils.dependencies import get_current_organization

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://slotbooking.cernsystem.com",
    ],
    allow_origin_regex=r"https://.*\.cernsystem\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-Org-Slug"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(super_admin.router)
app.include_router(public.router)


@app.get("/")
def root():
    return {"message": "Slot Booking API Running - Dynamic Time-Based Booking"}


@app.get("/organization/details")
def get_organization_details(
    request: Request,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Returns current organization details based on subdomain."""
    return {
        "id": current_org.id,
        "name": current_org.name,
        "slug": current_org.subdomain,
        "subdomain": current_org.subdomain,
        "is_active": current_org.is_active
    }
