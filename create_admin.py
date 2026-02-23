from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.hash import hash_password
from datetime import datetime
import pytz

db = SessionLocal()

admin = User(
    name="Admin1",
    email="admin1@gmail.com",
    password=hash_password("admin123"),
    role=UserRole.admin,
    created_at=datetime.now(pytz.timezone('Asia/Kolkata'))
)

db.add(admin)
db.commit()
db.close()

print("Admin created successfully")