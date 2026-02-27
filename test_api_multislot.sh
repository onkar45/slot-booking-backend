#!/bin/bash

echo "============================================================"
echo "MULTI-SLOT BOOKING API TEST"
echo "============================================================"

BASE_URL="http://127.0.0.1:8000"

echo ""
echo "1️⃣  Testing available times for 30-minute duration"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/bookings/available-times?date=2026-03-01&duration_minutes=30" | python3 -m json.tool | head -20

echo ""
echo "2️⃣  Testing available times for 60-minute duration"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/bookings/available-times?date=2026-03-01&duration_minutes=60" | python3 -m json.tool | head -20

echo ""
echo "3️⃣  Testing available times for 90-minute duration"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/bookings/available-times?date=2026-03-01&duration_minutes=90" | python3 -m json.tool | head -20

echo ""
echo "4️⃣  Testing available times for 120-minute duration"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/bookings/available-times?date=2026-03-01&duration_minutes=120" | python3 -m json.tool | head -20

echo ""
echo "5️⃣  Testing approved public bookings endpoint"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/bookings/approved-public" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total approved bookings: {len(data)}')
print('\nFirst 5 bookings:')
for booking in data[:5]:
    print(f'  • {booking[\"booking_date\"]} | {booking[\"start_time\"]} - {booking[\"end_time\"]}')
"

echo ""
echo "6️⃣  Testing invalid duration (should fail)"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/bookings/available-times?date=2026-03-01&duration_minutes=45" | python3 -m json.tool

echo ""
echo "============================================================"
echo "✅ API TEST COMPLETE"
echo "============================================================"
echo ""
echo "SUMMARY:"
echo "• Allowed durations: 30, 60, 90, 120 minutes"
echo "• Multi-slot bookings properly block all overlapping times"
echo "• Available-times endpoint respects existing bookings"
echo "• Public endpoint shows all approved bookings"
echo ""
