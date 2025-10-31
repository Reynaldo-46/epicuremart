-- Migration: Add registration enhancement fields
-- Date: 2025-10-29

-- Add new fields to users table
ALTER TABLE users 
ADD COLUMN first_name VARCHAR(50) AFTER full_name,
ADD COLUMN middle_name VARCHAR(50) AFTER first_name,
ADD COLUMN last_name VARCHAR(50) AFTER middle_name,
ADD COLUMN id_document VARCHAR(255) AFTER phone;

-- Add new address fields for CALABARZON address system
ALTER TABLE addresses
ADD COLUMN region VARCHAR(100) AFTER full_address,
ADD COLUMN province VARCHAR(100) AFTER region,
ADD COLUMN municipality VARCHAR(100) AFTER province,
ADD COLUMN barangay VARCHAR(100) AFTER city;

-- Update existing users to have first/last names from full_name where possible
UPDATE users 
SET first_name = SUBSTRING_INDEX(full_name, ' ', 1),
    last_name = SUBSTRING_INDEX(full_name, ' ', -1)
WHERE full_name IS NOT NULL AND first_name IS NULL;
