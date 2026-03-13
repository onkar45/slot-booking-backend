from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.hash import hash_password
from datetime import datetime
import pytz

db = SessionLocal()

# Check if super admin already exists
existing_super_admin = db.query(User).filter(User.role == UserRole.super_admin).first()

if existing_super_admin:
    print("Super Admin already exists with email:", existing_super_admin.email)
else:
    # Create super admin
    super_admin = User(
        name="SuperAdmin",
        email="superadmin@example.com",
        password=hash_password("admin123"),  # Replace with a strong password later
        role=UserRole.super_admin,
        created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
    )

    db.add(super_admin)
    db.commit()
    print("Super Admin created successfully. Email: superadmin@example.com, Password: admin123")

db.close()
