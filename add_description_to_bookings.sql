-- Migration: Add description field to bookings table
-- Date: 2026-03-02
-- Description: Add optional description field to allow users to provide booking notes

-- Add description column to bookings table
ALTER TABLE bookings 
ADD COLUMN description TEXT NULL;

-- Add comment to document the column
ALTER TABLE bookings 
MODIFY COLUMN description TEXT NULL COMMENT 'Optional user description for the booking (max 500 chars)';

-- Verify the change
DESCRIBE bookings;
