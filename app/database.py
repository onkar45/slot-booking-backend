from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
        
        
        
        
        
        
        
        
        
        
CREATE USER 'bookinguser'@'localhost' IDENTIFIED BY 'MahitNahi@12';
GRANT ALL PRIVILEGES ON slot_booking_db.* TO 'bookinguser'@'localhost';
FLUSH PRIVILEGES;
EXIT;



ssh root@192.46.213.87
cd ~/slot-booking-backend


0af52eb334a03a2c.vercel-dns-017.com.source venv/bin/activate
