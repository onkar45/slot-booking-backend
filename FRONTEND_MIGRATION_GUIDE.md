# Frontend Migration Guide

## Overview
The backend has been refactored from slot-based to dynamic time-based booking. Your frontend needs to be updated accordingly.

## Error You're Seeing
```
GET http://127.0.0.1:8000/slots/public 404 (Not Found)
```

This is because the `/slots/public` endpoint no longer exists.

---

## Changes Required in Frontend

### 1. Remove Slot Fetching Logic

**OLD CODE (WeeklyCalendar.jsx):**
```javascript
// ❌ Remove this
const fetchSlots = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/slots/public');
    setSlots(response.data);
  } catch (error) {
    console.error('Error fetching slots:', error);
  }
};
```

**NEW APPROACH:**
Instead of fetching pre-created slots, you now:
1. Let users pick a date and time
2. Check available times for that date
3. Create booking directly

---

### 2. New Booking Flow

#### Step 1: User Selects Date and Duration
```javascript
const [selectedDate, setSelectedDate] = useState(null);
const [duration, setDuration] = useState(30); // minutes
const [availableSlots, setAvailableSlots] = useState([]);
```

#### Step 2: Fetch Available Times
```javascript
const fetchAvailableTimes = async (date, durationMinutes) => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/bookings/available-times`,
      {
        params: {
          date: date, // Format: "2026-02-28"
          duration_minutes: durationMinutes
        },
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );
    setAvailableSlots(response.data.available_slots);
  } catch (error) {
    console.error('Error fetching available times:', error);
  }
};

// Call when date or duration changes
useEffect(() => {
  if (selectedDate) {
    fetchAvailableTimes(selectedDate, duration);
  }
}, [selectedDate, duration]);
```

#### Step 3: Create Booking
```javascript
const createBooking = async (date, startTime, durationMinutes) => {
  try {
    const response = await axios.post(
      'http://127.0.0.1:8000/bookings/',
      {
        date: date,              // "2026-02-28"
        start_time: startTime,   // "10:00:00"
        duration_minutes: durationMinutes
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    alert('Booking created successfully!');
    // Refresh bookings list
    fetchMyBookings();
  } catch (error) {
    if (error.response?.data?.detail) {
      alert(error.response.data.detail);
    } else {
      alert('Failed to create booking');
    }
  }
};
```

---

### 3. Updated Component Structure

**WeeklyCalendar.jsx - Suggested Refactor:**

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const WeeklyCalendar = () => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [duration, setDuration] = useState(30);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const token = localStorage.getItem('token'); // or however you store it
  const API_BASE = 'http://127.0.0.1:8000';

  // Fetch user's bookings
  const fetchMyBookings = async () => {
    try {
      const response = await axios.get(`${API_BASE}/bookings/my-bookings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMyBookings(response.data);
    } catch (error) {
      console.error('Error fetching bookings:', error);
    }
  };

  // Fetch available times for selected date
  const fetchAvailableTimes = async () => {
    if (!selectedDate) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/bookings/available-times`, {
        params: {
          date: selectedDate,
          duration_minutes: duration
        },
        headers: { Authorization: `Bearer ${token}` }
      });
      setAvailableSlots(response.data.available_slots);
    } catch (error) {
      console.error('Error fetching available times:', error);
      setAvailableSlots([]);
    } finally {
      setLoading(false);
    }
  };

  // Create booking
  const handleBookSlot = async (startTime) => {
    try {
      await axios.post(
        `${API_BASE}/bookings/`,
        {
          date: selectedDate,
          start_time: startTime,
          duration_minutes: duration
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      alert('Booking created successfully!');
      fetchMyBookings();
      fetchAvailableTimes(); // Refresh available slots
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to create booking';
      alert(message);
    }
  };

  useEffect(() => {
    fetchMyBookings();
  }, []);

  useEffect(() => {
    fetchAvailableTimes();
  }, [selectedDate, duration]);

  return (
    <div className="weekly-calendar">
      <h2>Book a Time Slot</h2>
      
      {/* Date Picker */}
      <div className="date-picker">
        <label>Select Date:</label>
        <input
          type="date"
          value={selectedDate || ''}
          onChange={(e) => setSelectedDate(e.target.value)}
          min={new Date().toISOString().split('T')[0]}
        />
      </div>

      {/* Duration Selector */}
      <div className="duration-selector">
        <label>Duration (minutes):</label>
        <select value={duration} onChange={(e) => setDuration(Number(e.target.value))}>
          <option value={5}>5 minutes</option>
          <option value={15}>15 minutes</option>
          <option value={30}>30 minutes</option>
          <option value={45}>45 minutes</option>
          <option value={60}>60 minutes</option>
        </select>
      </div>

      {/* Available Slots */}
      {selectedDate && (
        <div className="available-slots">
          <h3>Available Times for {selectedDate}</h3>
          {loading ? (
            <p>Loading...</p>
          ) : availableSlots.length > 0 ? (
            <div className="slots-grid">
              {availableSlots.map((slot, index) => (
                <button
                  key={index}
                  className="slot-button"
                  onClick={() => handleBookSlot(slot.start_time + ':00')}
                >
                  {slot.start_time} - {slot.end_time}
                </button>
              ))}
            </div>
          ) : (
            <p>No available slots for this date and duration</p>
          )}
        </div>
      )}

      {/* My Bookings */}
      <div className="my-bookings">
        <h3>My Bookings</h3>
        {myBookings.length > 0 ? (
          <ul>
            {myBookings.map((booking) => (
              <li key={booking.id}>
                <strong>{booking.date}</strong> | 
                {booking.start_time} - {booking.end_time} | 
                <span className={`status-${booking.status}`}>
                  {booking.status}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No bookings yet</p>
        )}
      </div>
    </div>
  );
};

export default WeeklyCalendar;
```

---

### 4. Admin Panel Updates

If you have an admin panel that manages slots, update it to manage bookings instead:

**OLD:** Admin creates slots → Users book slots
**NEW:** Users create bookings → Admin approves/rejects

```javascript
// Fetch all bookings (admin)
const fetchAllBookings = async () => {
  const response = await axios.get(`${API_BASE}/bookings/`, {
    headers: { Authorization: `Bearer ${adminToken}` }
  });
  return response.data;
};

// Approve booking
const approveBooking = async (bookingId) => {
  await axios.put(
    `${API_BASE}/bookings/${bookingId}/approve`,
    {},
    { headers: { Authorization: `Bearer ${adminToken}` } }
  );
};

// Reject booking
const rejectBooking = async (bookingId) => {
  await axios.put(
    `${API_BASE}/bookings/${bookingId}/reject`,
    {},
    { headers: { Authorization: `Bearer ${adminToken}` } }
  );
};
```

---

### 5. Data Format Changes

**OLD Booking Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "slot_id": 123,
  "status": "pending",
  "slot": {
    "id": 123,
    "date": "2026-02-28",
    "start_time": "10:00:00",
    "end_time": "10:30:00"
  }
}
```

**NEW Booking Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "date": "2026-02-28",
  "start_time": "10:00:00",
  "end_time": "10:30:00",
  "status": "pending",
  "user": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Update your code to access:**
- `booking.date` instead of `booking.slot.date`
- `booking.start_time` instead of `booking.slot.start_time`
- `booking.end_time` instead of `booking.slot.end_time`

---

## Quick Fix for Immediate Error

If you want to quickly stop the 404 errors while you refactor:

1. Comment out the slot fetching code:
```javascript
// const fetchSlots = async () => { ... };
```

2. Remove the useEffect that calls it:
```javascript
// useEffect(() => {
//   fetchSlots();
// }, []);
```

3. Add a temporary message:
```javascript
return (
  <div>
    <h2>Booking System Updated</h2>
    <p>The booking system has been upgraded to dynamic time-based booking.</p>
    <p>Please update the frontend to use the new API.</p>
  </div>
);
```

---

## Testing the New API

Use these curl commands to test the backend:

```bash
# Get available times
curl -X GET "http://127.0.0.1:8000/bookings/available-times?date=2026-02-28&duration_minutes=30" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create booking
curl -X POST "http://127.0.0.1:8000/bookings/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-28",
    "start_time": "10:00:00",
    "duration_minutes": 30
  }'

# Get my bookings
curl -X GET "http://127.0.0.1:8000/bookings/my-bookings" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Summary of Changes

| Old Approach | New Approach |
|-------------|--------------|
| Admin creates slots | No slot creation needed |
| User selects from pre-created slots | User picks date + time + duration |
| `/slots/public` endpoint | `/bookings/available-times` endpoint |
| `POST /bookings/` with `slot_id` | `POST /bookings/` with `date`, `start_time`, `duration_minutes` |
| `booking.slot.date` | `booking.date` |
| `booking.slot.start_time` | `booking.start_time` |

---

## Need Help?

If you share your frontend code (WeeklyCalendar.jsx and related files), I can provide specific refactoring instructions for your exact implementation.
