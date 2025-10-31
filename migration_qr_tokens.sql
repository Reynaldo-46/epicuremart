-- Migration to add QR token columns for pickup and delivery tracking
-- Run this migration to enable QR code functionality for courier pickup and rider delivery

ALTER TABLE orders 
ADD COLUMN pickup_token VARCHAR(500) NULL AFTER rider_id,
ADD COLUMN delivery_token VARCHAR(500) NULL AFTER pickup_token;
