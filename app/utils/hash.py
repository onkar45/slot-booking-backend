import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    # Hash with SHA256 first to handle any length, then bcrypt the result
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(password_hash)

def verify_password(plain, hashed):
    # Hash with SHA256 first to handle any length, then verify with bcrypt
    password_hash = hashlib.sha256(plain.encode('utf-8')).hexdigest()
    return pwd_context.verify(password_hash, hashed)