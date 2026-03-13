from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.hash import hash_password

db = SessionLocal()

# Find superadmin user
superadmin = db.query(User).filter(User.role == UserRole.super_admin).first()

if superadmin:
    # Update credentials
    superadmin.email = "superadmin@gmail.com"
    superadmin.password = hash_password("Superadmin@123")
    superadmin.name = "SuperAdmin"
    
    db.commit()
    print("✅ SuperAdmin credentials updated successfully!")
    print(f"   Email: superadmin@gmail.com")
    print(f"   Password: Superadmin@123")
else:
    # Create new superadmin if doesn't exist
    new_superadmin = User(
        name="SuperAdmin",
        email="superadmin@gmail.com",
        password=hash_password("Superadmin@123"),
        role=UserRole.super_admin,
        is_active=True
    )
    db.add(new_superadmin)
    db.commit()
    print("✅ SuperAdmin created successfully!")
    print(f"   Email: superadmin@gmail.com")
    print(f"   Password: Superadmin@123")

db.close()
