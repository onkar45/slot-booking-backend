# Dynamic Time-Based Booking API

## Overview
This API supports dynamic time-based bookings without requiring pre-created slots.

## Business Rules

- **Business Hours**: 09:00 AM - 09:00 PM
- **Duration Range**: 5 - 60 minutes
- **Overlap Prevention**: System automatically prevents overlapping bookings for the same user
- **Auto-Expiry**: Pending bookings are automatically marked as expired after their end time passes

## Endpoints

### 1. Create Booking
**POST** `/bookings/`

Create a new booking with dynamic time selection.

**Request Body:**
```json
{
  "date": "2026-02-28",
  "start_time": "10:00:00",
  "duration_minutes": 30
}
```

**Validations:**
- `date`: Must be today or future date
- `duration_minutes`: Must be between 5 and 60
- Booking must be within business hours (09:00 AM - 09:00 PM)
- No overlapping bookings for the same user

**Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "date": "2026-02-28",
  "start_time": "10:00:00",
  "end_time": "10:30:00",
  "status": "pending",
  "created_at": "2026-02-26T11:30:00",
  "user": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Error Responses:**
- `400`: Duration out of range
- `400`: Past date
- `400`: Outside business hours
- `400`: Overlapping booking exists

---

### 2. Get My Bookings
**GET** `/bookings/my-bookings`

Get current user's bookings (excludes bookings older than 2 days).

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 5,
    "date": "2026-02-28",
    "start_time": "10:00:00",
    "end_time": "10:30:00",
    "status": "pending",
    "created_at": "2026-02-26T11:30:00",
    "user": { ... }
  }
]
```

---

### 3. Get All Bookings (Admin)
**GET** `/bookings/`

Get all bookings (admin only, excludes bookings older than 2 days).

**Authorization:** Admin role required

**Response:** Same as "Get My Bookings"

---

### 4. Get Active Bookings
**GET** `/bookings/active`

Get only active (approved and not expired) bookings for current user.

**Response:**
```json
{
  "active_count": 2,
  "active_bookings": [
    {
      "id": 1,
      "user_id": 5,
      "date": "2026-02-28",
      "start_time": "10:00:00",
      "end_time": "10:30:00",
      "status": "approved",
      "created_at": "2026-02-26T11:30:00",
      "user": { ... }
    }
  ]
}
```

---

### 5. Check Available Times
**GET** `/bookings/available-times?date=2026-02-28&duration_minutes=30`

Get available time slots for a given date and duration.

**Query Parameters:**
- `date`: Date to check (YYYY-MM-DD)
- `duration_minutes`: Desired duration (5-60)

**Response:**
```json
{
  "date": "2026-02-28",
  "duration_minutes": 30,
  "available_slots": [
    {
      "start_time": "09:00",
      "end_time": "09:30"
    },
    {
      "start_time": "09:15",
      "end_time": "09:45"
    },
    {
      "start_time": "09:30",
      "end_time": "10:00"
    }
  ]
}
```

**Note:** Available slots are generated every 15 minutes within business hours, excluding times that overlap with existing bookings.

---

### 6. Approve Booking (Admin)
**PUT** `/bookings/{booking_id}/approve`

Approve a pending booking.

**Authorization:** Admin role required

**Response:**
```json
{
  "message": "Booking approved"
}
```

**Error Responses:**
- `404`: Booking not found
- `400`: Already approved/rejected/expired

---

### 7. Reject Booking (Admin)
**PUT** `/bookings/{booking_id}/reject`

Reject a pending booking.

**Authorization:** Admin role required

**Response:**
```json
{
  "message": "Booking rejected"
}
```

**Error Responses:**
- `404`: Booking not found
- `400`: Already approved/rejected

---

## Booking Status Flow

```
pending → approved (by admin)
pending → rejected (by admin)
pending → expired (automatic, when end time passes)
```

## Example Usage

### 1. User wants to book 30 minutes on Feb 28
```bash
# Check available times
curl -X GET "http://localhost:8000/bookings/available-times?date=2026-02-28&duration_minutes=30" \
  -H "Authorization: Bearer {token}"

# Create booking
curl -X POST "http://localhost:8000/bookings/" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-28",
    "start_time": "10:00:00",
    "duration_minutes": 30
  }'
```

### 2. Admin approves booking
```bash
curl -X PUT "http://localhost:8000/bookings/1/approve" \
  -H "Authorization: Bearer {admin_token}"
```

### 3. User checks active bookings
```bash
curl -X GET "http://localhost:8000/bookings/active" \
  -H "Authorization: Bearer {token}"
```
