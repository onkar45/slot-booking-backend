#!/usr/bin/env python3
"""Quick script to check approved bookings in the database."""

from app.database import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.user import User  # Import User model to resolve relationship

def main():
    db = SessionLocal()
    try:
        # Count all bookings
        total_bookings = db.query(Booking).count()
        print(f"📊 Total bookings in database: {total_bookings}")
        
        # Count by status
        pending = db.query(Booking).filter(Booking.status == BookingStatus.pending).count()
        approved = db.query(Booking).filter(Booking.status == BookingStatus.approved).count()
        rejected = db.query(Booking).filter(Booking.status == BookingStatus.rejected).count()
        expired = db.query(Booking).filter(Booking.status == BookingStatus.expired).count()
        
        print(f"\n📈 Bookings by status:")
        print(f"  ⏳ Pending: {pending}")
        print(f"  ✅ Approved: {approved}")
        print(f"  ❌ Rejected: {rejected}")
        print(f"  ⏰ Expired: {expired}")
        
        # Show approved bookings
        if approved > 0:
            print(f"\n✅ Approved bookings (shown on landing page):")
            approved_bookings = db.query(Booking).filter(
                Booking.status == BookingStatus.approved
            ).order_by(Booking.date, Booking.start_time).all()
            
            for booking in approved_bookings:
                print(f"  • ID: {booking.id} | Date: {booking.date} | Time: {booking.start_time} - {booking.end_time}")
        else:
            print(f"\n⚠️  No approved bookings found!")
            print(f"   This is why the landing page is empty.")
            print(f"\n💡 To fix this:")
            print(f"   1. Create a booking as a user")
            print(f"   2. Login as admin and approve it")
            print(f"   3. Then it will appear on the landing page")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
