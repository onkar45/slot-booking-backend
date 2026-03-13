from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, bookings, admin, public, super_admin
from app.models import user, booking, blocked_date, login_activity

app = FastAPI()

origins = [
    # "https://www.cernsystem.com",
    # "https://cernsystem.com",
    # "https://slotbooking.cernsystem.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
