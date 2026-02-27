# Complete API Endpoints Reference

Base URL: `http://127.0.0.1:8000`

---

## 🌐 Public Endpoints (No Authentication Required)

### 1. Root
```
GET /
```
**Response:**
```json
{
  "message": "Slot Booking API Running - Dynamic Time-Based Booking"
}
```

---

### 2. Get Available Times
```
GET /bookings/available-times?date=2026-02-28&duration_minutes=30
```
**Query Parameters:**
- `date` (required): Date in YYYY-MM-DD format
- `duration_minutes` (required): Duration between 5-60 minutes

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
    }
  ]
}
```

---

### 3. Get Approved Bookings (Public)
```
GET /bookings/approved-public
```
**Response:**
```json
[
  {
    "id": 1,
    "booking_date": "2026-02-26",
    "start_time": "14:00:00",
    "end_time": "14:30:00"
  }
]
```

---

### 4. Get Approved Bookings Count
```
GET /bookings/approved-count
```
**Response:**
```json
{
  "approved_count": 10
}
```

---

### 5. Debug Bookings (Development)
```
GET /bookings/debug-bookings
```
**Response:**
```json
{
  "total_bookings": 26,
  "approved_bookings": 10,
  "sample_booking": {
    "id": 17,
    "date": "2026-02-26",
    "start_time": "15:00:00",
    "end_time": "16:00:00",
    "status": "approved"
  },
  "all_approved_ids": [17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
}
```

---

## 🔐 Authentication Endpoints

### 6. Register User
```
POST /auth/register
```
**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```
**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-02-26T10:00:00"
}
```

---

### 7. Login
```
POST /auth/login
```
**Request Body (Form Data):**
```
username: john@example.com
password: password123
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 8. Get Current User
```
GET /auth/me
```
**Headers:**
```
Authorization: Bearer {token}
```
**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-02-26T10:00:00"
}
```

---

## 📅 Booking Endpoints (Authenticated)

### 9. Create Booking
```
POST /bookings/
```
**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```
**Request Body:**
```json
{
  "date": "2026-02-28",
  "start_time": "10:00:00",
  "duration_minutes": 30
}
```

**⚠️ IMPORTANT - Request Format:**
- ✅ **CORRECT**: Send `duration_minutes` (30, 60, 90, or 120)
- ❌ **WRONG**: Do NOT send `end_time` or `description` fields
- The API calculates `end_time` automatically from `start_time + duration_minutes`

**Allowed Durations:**
- `30` minutes = 1 slot
- `60` minutes = 1 slot
- `90` minutes = 1.5 slots
- `120` minutes = 2 slots

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

---

### 10. Get My Bookings
```
GET /bookings/my-bookings
```
**Headers:**
```
Authorization: Bearer {token}
```
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
    "user": {
      "id": 5,
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
]
```

---

### 11. Get Active Bookings
```
GET /bookings/active
```
**Headers:**
```
Authorization: Bearer {token}
```
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
      "user": {
        "id": 5,
        "name": "John Doe",
        "email": "john@example.com"
      }
    }
  ]
}
```

---

## 👑 Admin Endpoints (Admin Only)

### 12. Get All Bookings
```
GET /bookings/
```
**Headers:**
```
Authorization: Bearer {admin_token}
```
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
    "user": {
      "id": 5,
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
]
```

---

### 13. Approve Booking
```
PUT /bookings/{booking_id}/approve
```
**Headers:**
```
Authorization: Bearer {admin_token}
```
**Response:**
```json
{
  "message": "Booking approved"
}
```

---

### 14. Reject Booking
```
PUT /bookings/{booking_id}/reject
```
**Headers:**
```
Authorization: Bearer {admin_token}
```
**Response:**
```json
{
  "message": "Booking rejected"
}
```

---

### 15. Get All Users
```
GET /admin/users
```
**Headers:**
```
Authorization: Bearer {admin_token}
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2026-02-26T10:00:00"
  }
]
```

---

### 16. Create User (Admin)
```
POST /admin/users
```
**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```
**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "password123",
  "role": "user"
}
```
**Response:**
```json
{
  "id": 2,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-02-26T10:00:00"
}
```

---

### 17. Update User
```
PATCH /admin/users/{user_id}
```
**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```
**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "is_active": true
}
```
**Response:**
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-02-26T10:00:00"
}
```

---

### 18. Activate User
```
PUT /admin/users/{user_id}/activate
```
**Headers:**
```
Authorization: Bearer {admin_token}
```
**Response:**
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-02-26T10:00:00"
}
```

---

### 19. Deactivate User
```
PUT /admin/users/{user_id}/deactivate
```
**Headers:**
```
Authorization: Bearer {admin_token}
```
**Response:**
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "role": "user",
  "is_active": false,
  "created_at": "2026-02-26T10:00:00"
}
```

---

### 20. Delete User
```
DELETE /admin/users/{user_id}
```
**Headers:**
```
Authorization: Bearer {admin_token}
```
**Response:** `204 No Content`

---

## 📊 Summary

| Category | Count | Authentication |
|----------|-------|----------------|
| Public Endpoints | 5 | None |
| Auth Endpoints | 3 | None (for login/register) |
| User Booking Endpoints | 3 | User token required |
| Admin Booking Endpoints | 3 | Admin token required |
| Admin User Management | 6 | Admin token required |
| **Total** | **20** | - |

---

## 🔑 Authentication Flow

1. **Register**: `POST /auth/register`
2. **Login**: `POST /auth/login` → Get token
3. **Use Token**: Add `Authorization: Bearer {token}` header to requests
4. **Verify**: `GET /auth/me` to check current user

---

## 🚀 Quick Test Commands

```bash
# Test public endpoint
curl http://127.0.0.1:8000/bookings/approved-public

# Test with authentication
curl -X GET http://127.0.0.1:8000/bookings/my-bookings \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create booking
curl -X POST http://127.0.0.1:8000/bookings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-28",
    "start_time": "10:00:00",
    "duration_minutes": 30
  }'
```

---

## 📝 Notes

- All times are in 24-hour format (HH:MM:SS)
- All dates are in ISO format (YYYY-MM-DD)
- Business hours: 09:00 AM - 09:00 PM
- Booking duration: 5-60 minutes
- Bookings older than 2 days are automatically hidden
- Pending bookings are automatically marked as expired after their end time
