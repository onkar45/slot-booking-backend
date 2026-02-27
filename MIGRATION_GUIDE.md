# Migration Guide: Slot-Based to Dynamic Time-Based Booking

## Overview
The booking system has been refactored from a pre-created slot-based system to a dynamic time-based booking system.

## What Changed

### 1. Database Schema
- Removed `slot_id` foreign key from `bookings` table
- Added `date`, `start_time`, `end_time` columns to `bookings` table
- Slots table is now optional (can be deprecated)

### 2. Booking Model
- No longer depends on Slot model
- Direct time-based fields: `date`, `start_time`, `end_time`

### 3. API Changes

#### Old Booking Request:
```json
{
  "slot_id": 123
}
```

#### New Booking Request:
```json
{
  "date": "2026-02-28",
  "start_time": "10:00:00",
  "duration_minutes": 30
}
```

### 4. Business Rules
- Business hours: 09:00 AM - 09:00 PM
- Duration: 5-60 minutes
- Automatic overlap detection
- No need for admin to create slots

### 5. New Endpoints

#### Check Available Times
```
GET /bookings/available-times?date=2026-02-28&duration_minutes=30
```
Returns available time slots for the given date and duration.

## Migration Steps

### Step 1: Backup Database
```bash
mysqldump -u root -p slot_booking_db > backup_before_migration.sql
```

### Step 2: Run Migration
```bash
./venv/bin/alembic upgrade head
```

This will:
- Add new columns (date, start_time, end_time) to bookings
- Remove slot_id foreign key
- Drop slot_id column

### Step 3: Restart Application
```bash
# Stop current server
# Start with: ./venv/bin/uvicorn app.main:app --reload
```

### Step 4: Update Frontend
Update your frontend to use the new booking API format.

## Rollback (if needed)

```bash
./venv/bin/alembic downgrade -1
```

## Notes

- Old slot-based bookings will be lost during migration (ensure backup)
- The slots router is removed from main.py
- Slots table can be kept for historical data or removed later
- Old migration scripts (add_expired_status.py, add_is_active_column.py) can be deleted
