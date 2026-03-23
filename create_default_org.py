"""
Seed script: Creates the default organization in the database.
Run once after migration: python create_default_org.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
# Import all models so SQLAlchemy can resolve relationships
from app.models import user, booking, blocked_date, login_activity
from app.models.organization import Organization

def create_default_org():
    db = SessionLocal()
    try:
        existing = db.query(Organization).filter(Organization.subdomain == "default").first()
        if existing:
            print(f"✅ Default organization already exists (id={existing.id})")
            return

        org = Organization(name="Default Organization", subdomain="default", is_active=True)
        db.add(org)
        db.commit()
        db.refresh(org)
        print(f"✅ Default organization created (id={org.id}, subdomain='default')")
    finally:
        db.close()

if __name__ == "__main__":
    create_default_org()
