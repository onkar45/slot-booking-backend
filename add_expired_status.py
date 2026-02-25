"""
Migration script to add 'expired' status to bookings table.
Run this once to update your existing database.

Usage: python3 add_expired_status.py (from within venv)
"""
from app.database import engine
from sqlalchemy import text

def add_expired_status():
    with engine.connect() as conn:
        try:
            # For MySQL, modify the ENUM to include 'expired'
            conn.execute(text(
                "ALTER TABLE bookings MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'expired') DEFAULT 'pending'"
            ))
            conn.commit()
            print("✓ Successfully added 'expired' status to bookings table")
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate" in error_msg or "already" in error_msg:
                print("✓ Status 'expired' already exists")
            else:
                print(f"✗ Error: {e}")
                raise

if __name__ == "__main__":
    add_expired_status()
