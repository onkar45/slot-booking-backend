# Public Endpoint Update - Available Times

## Change Summary

The `/bookings/available-times` endpoint has been made public (no authentication required).

## Updated Endpoint

**GET** `/bookings/available-times`

### Authentication
- ❌ **No authentication required** (previously required)
- ✅ Public access for homepage calendar

### Parameters
- `date` (query param, required): Date in YYYY-MM-DD format
- `duration_minutes` (query param, required): Duration between 5-60 minutes

### Response
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

### Business Logic (Unchanged)
- ✅ Business hours: 09:00 AM - 09:00 PM
- ✅ Duration validation: 5-60 minutes
- ✅ Past date validation
- ✅ Overlap detection with all existing bookings
- ✅ 15-minute interval slots

### Key Changes

**Before:**
```python
def get_available_times(
    date: dt_date,
    duration_minutes: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ❌ Required auth
):
    # Only checked current user's bookings
    existing_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        ...
    )
```

**After:**
```python
def get_available_times(
    date: dt_date,
    duration_minutes: int,
    db: Session = Depends(get_db)  # ✅ No auth required
):
    # Checks ALL users' bookings
    existing_bookings = db.query(Booking).filter(
        Booking.date == date,
        ...
    )
```

### Usage Example

**Frontend (No token needed):**
```javascript
// Public access - no authentication header required
const response = await axios.get(
  'http://127.0.0.1:8000/bookings/available-times',
  {
    params: {
      date: '2026-02-28',
      duration_minutes: 30
    }
  }
);

console.log(response.data.available_slots);
```

**cURL:**
```bash
# No Authorization header needed
curl -X GET "http://127.0.0.1:8000/bookings/available-times?date=2026-02-28&duration_minutes=30"
```

### Other Endpoints (Unchanged)

All other booking endpoints still require authentication:
- ✅ `POST /bookings/` - Requires auth
- ✅ `GET /bookings/my-bookings` - Requires auth
- ✅ `GET /bookings/` - Requires admin auth
- ✅ `GET /bookings/active` - Requires auth
- ✅ `PUT /bookings/{id}/approve` - Requires admin auth
- ✅ `PUT /bookings/{id}/reject` - Requires admin auth

### Testing

```bash
# Test without authentication (should work)
curl "http://127.0.0.1:8000/bookings/available-times?date=2026-02-28&duration_minutes=30"

# Should return available slots, not 401 Unauthorized
```

### Notes

- The endpoint now checks ALL bookings (from all users) to determine availability
- This prevents double-booking across different users
- Previously it only showed times available for the authenticated user
- Now it shows globally available times for anyone to see
