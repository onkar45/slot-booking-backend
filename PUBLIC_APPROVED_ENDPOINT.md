# Public Approved Bookings Endpoint

## New Endpoint Created

**GET** `/bookings/approved-public`

### Authentication
- ✅ **No authentication required** (Public endpoint)
- Anyone can view approved bookings

### Purpose
Display approved bookings on the public homepage calendar without exposing sensitive user information.

### Response Schema

```python
class PublicBookingResponse(BaseModel):
    """Public response schema - no sensitive user information."""
    id: int
    date: date
    start_time: time
    end_time: time
```

### Response Example

```json
[
  {
    "id": 1,
    "date": "2026-02-26",
    "start_time": "14:00:00",
    "end_time": "15:00:00"
  },
  {
    "id": 2,
    "date": "2026-02-27",
    "start_time": "10:00:00",
    "end_time": "10:30:00"
  }
]
```

### What's Included
- ✅ Booking ID
- ✅ Date
- ✅ Start time
- ✅ End time

### What's NOT Included (Security)
- ❌ User email
- ❌ User password
- ❌ User role
- ❌ User name
- ❌ User ID
- ❌ Booking status (only approved shown)
- ❌ Created timestamp

### Implementation

#### Schema (app/schemas/booking.py)
```python
class PublicBookingResponse(BaseModel):
    """Public response schema - no sensitive user information."""
    id: int
    date: date
    start_time: time
    end_time: time

    class Config:
        from_attributes = True
```

#### Router (app/routers/bookings.py)
```python
@router.get("/approved-public", response_model=list[PublicBookingResponse])
def get_approved_bookings_public(
    db: Session = Depends(get_db)
):
    """
    Get all approved bookings (Public endpoint).
    Returns only approved bookings without sensitive user information.
    No authentication required.
    """
    
    approved_bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.approved
    ).order_by(Booking.date, Booking.start_time).all()
    
    return approved_bookings
```

### Usage

#### Frontend (No authentication needed)
```javascript
// Fetch approved bookings for calendar display
const response = await axios.get(
  'http://127.0.0.1:8000/bookings/approved-public'
);

console.log(response.data);
// [
//   { id: 1, date: "2026-02-26", start_time: "14:00:00", end_time: "15:00:00" },
//   { id: 2, date: "2026-02-27", start_time: "10:00:00", end_time: "10:30:00" }
// ]
```

#### cURL
```bash
# No Authorization header needed
curl -X GET "http://127.0.0.1:8000/bookings/approved-public"
```

### Query Details

- **Filter**: Only bookings with `status = "approved"`
- **Order**: Sorted by date (ascending), then start_time (ascending)
- **Returns**: All approved bookings (no pagination)

### Use Cases

1. **Homepage Calendar**: Display occupied time slots
2. **Public Schedule**: Show when facility is booked
3. **Availability Check**: Cross-reference with available-times endpoint

### Security Considerations

✅ **Safe to expose publicly:**
- Only shows approved bookings
- No user identification possible
- No sensitive data exposed
- Read-only operation

❌ **Does NOT expose:**
- Who made the booking
- Contact information
- Pending/rejected bookings
- Internal booking details

### Testing

```bash
# Test the endpoint
curl http://127.0.0.1:8000/bookings/approved-public

# Should return array of approved bookings
# No 401 Unauthorized error
```

### Related Endpoints

| Endpoint | Auth Required | Purpose |
|----------|---------------|---------|
| `GET /bookings/approved-public` | ❌ No | Public approved bookings |
| `GET /bookings/available-times` | ❌ No | Check available slots |
| `POST /bookings/` | ✅ Yes | Create booking |
| `GET /bookings/my-bookings` | ✅ Yes | User's bookings |
| `GET /bookings/` | ✅ Admin | All bookings (admin) |

### Integration Example

```javascript
// Homepage calendar component
async function loadCalendarData() {
  // Get approved bookings (occupied slots)
  const approvedBookings = await axios.get(
    'http://127.0.0.1:8000/bookings/approved-public'
  );
  
  // Get available times for selected date
  const availableTimes = await axios.get(
    'http://127.0.0.1:8000/bookings/available-times',
    { params: { date: '2026-02-28', duration_minutes: 30 } }
  );
  
  // Render calendar with both datasets
  renderCalendar(approvedBookings.data, availableTimes.data);
}
```
