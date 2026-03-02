# Booking Cancellation Implementation

## ✅ Implementation Complete - APPROACH 2 (PATCH)

### Changes Made:

## 1. Database Migration
**Files Created:**
- `add_cancellation_fields.sql` - SQL migration
- `alembic/versions/add_cancellation_tracking.py` - Alembic migration

**Schema Changes:**
```sql
-- Added 'cancelled' to status enum
status ENUM('pending', 'approved', 'rejected', 'expired', 'cancelled')

-- Added tracking fields
cancelled_at DATETIME NULL
cancelled_by INT NULL (foreign key to users.id)
```

---

## 2. Model Updated
**File:** `app/models/booking.py`

**Changes:**
```python
class BookingStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"
    cancelled = "cancelled"  # NEW

class Booking(Base):
    # ... existing fields ...
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by])
```

---

## 3. New Endpoint Added
**File:** `app/routers/bookings.py`

**Endpoint:** `PATCH /bookings/{booking_id}/cancel`

**Features:**
- ✅ User can cancel their own bookings
- ✅ Admin can cancel any booking
- ✅ Records who cancelled and when
- ✅ Prevents cancelling past bookings
- ✅ Prevents cancelling already cancelled bookings
- ✅ Prevents cancelling rejected bookings
- ✅ Uses Asia/Kolkata timezone

---

## 4. API Usage

### Cancel Booking
```bash
curl -X PATCH http://127.0.0.1:8000/bookings/123/cancel \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Response (200):**
```json
{
  "message": "Booking cancelled successfully",
  "booking_id": 123,
  "cancelled_at": "2026-03-02T14:30:00",
  "cancelled_by": "John Doe"
}
```

**Error Responses:**
- `404` - Booking not found
- `403` - Not authorized to cancel this booking
- `400` - Booking already cancelled
- `400` - Cannot cancel rejected booking
- `400` - Cannot cancel past bookings

---

## 5. Authorization Rules

| User Type | Can Cancel |
|-----------|------------|
| Regular User | Only their own bookings |
| Admin | Any booking |

---

## 6. Validation Rules

**Can Cancel:**
- ✅ Status is "pending" or "approved"
- ✅ Booking is in the future
- ✅ User owns the booking OR user is admin

**Cannot Cancel:**
- ❌ Status is "cancelled" (already cancelled)
- ❌ Status is "rejected" (rejected bookings)
- ❌ Booking end time has passed
- ❌ User doesn't own booking (unless admin)

---

## 7. Updated Endpoints

### GET /bookings/my-bookings
- Now includes cancelled bookings
- Shows cancellation info if cancelled

### GET /bookings/ (Admin)
- Now includes cancelled bookings
- Shows who cancelled and when

### GET /bookings/active
- Excludes cancelled bookings
- Only shows approved, future bookings

---

## 8. Frontend Integration

**Update your frontend to use:**
```javascript
// Cancel booking
await api.patch(`/bookings/${bookingId}/cancel`);
```

**Instead of:**
```javascript
// Old DELETE approach (don't use)
await api.delete(`/bookings/${bookingId}`);
```

---

## 9. Database Schema

```
bookings table:
├── id (PK)
├── user_id (FK → users.id)
├── date
├── start_time
├── end_time
├── status (pending/approved/rejected/expired/cancelled)
├── description
├── created_at
├── cancelled_at (NEW)
└── cancelled_by (FK → users.id) (NEW)
```

---

## 10. Benefits of This Approach

✅ **Audit Trail** - Know who cancelled and when
✅ **History** - Users can see cancelled bookings
✅ **Analytics** - Track cancellation patterns
✅ **Compliance** - Meet data retention requirements
✅ **Debugging** - Easier to troubleshoot issues
✅ **Undo** - Could restore cancelled bookings if needed

---

## 11. Testing

**Test Cases:**
1. ✅ User cancels their own pending booking
2. ✅ User cancels their own approved booking
3. ✅ Admin cancels any user's booking
4. ❌ User tries to cancel another user's booking (403)
5. ❌ User tries to cancel already cancelled booking (400)
6. ❌ User tries to cancel rejected booking (400)
7. ❌ User tries to cancel past booking (400)

---

## 12. Migration Applied

```bash
mysql -u root -p slot_booking_db < add_cancellation_fields.sql
```

**Verified:**
- ✅ Status enum includes 'cancelled'
- ✅ cancelled_at column added
- ✅ cancelled_by column added
- ✅ Foreign key constraint created

---

## 🎉 Implementation Complete!

Restart your backend server and the cancellation endpoint will be ready to use.

```bash
uvicorn app.main:app --reload
```
