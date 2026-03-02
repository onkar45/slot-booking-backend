-- Migration: Add cancellation tracking fields to bookings table
-- Date: 2026-03-02
-- Description: Add cancelled_at and cancelled_by fields for audit trail

-- Add cancelled status to enum
ALTER TABLE bookings 
MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'expired', 'cancelled') DEFAULT 'pending';

-- Add cancellation tracking columns
ALTER TABLE bookings 
ADD COLUMN cancelled_at DATETIME NULL,
ADD COLUMN cancelled_by INT NULL;

-- Add foreign key constraint for cancelled_by
ALTER TABLE bookings
ADD CONSTRAINT fk_cancelled_by_user
FOREIGN KEY (cancelled_by) REFERENCES users(id)
ON DELETE SET NULL;

-- Verify the changes
DESCRIBE bookings;
