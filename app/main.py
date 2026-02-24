from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, slots,bookings
from app.models import user

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(slots.router)
app.include_router(bookings.router)

@app.get("/")
def root():
    return {"message": "Slot Booking API Running"}