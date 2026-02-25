"""
Migration script to add is_active column to users table.
Run this once to update your existing database.

Usage: source venv/bin/activate && python3 add_is_active_column.py
"""
from app.database import engine
from sqlalchemy import text

def add_is_active_column():
    with engine.connect() as conn:
        try:
            # Add is_active column with default value True
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL"
            ))
            conn.commit()
            print("✓ Successfully added is_active column to users table")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "duplicate column" in error_msg:
                print("✓ Column is_active already exists")
            else:
                print(f"✗ Error: {e}")
                print("\nIf you're using SQLite, try this SQL command instead:")
                print("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;")
                raise

if __name__ == "__main__":
    add_is_active_column()
