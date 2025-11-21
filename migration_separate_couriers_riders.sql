-- Migration: Separate Couriers and Riders with Company Names
-- Date: 2025-11-20

-- 1. Add company_name field to users table for courier companies
ALTER TABLE users 
ADD COLUMN company_name VARCHAR(200) NULL AFTER quick_reply_templates;

-- 2. Rename courier_company_id to courier_id for clarity
-- Note: If courier_company_id already exists, we need to handle it
-- First, check if courier_company_id exists and rename it
ALTER TABLE users 
CHANGE COLUMN courier_company_id courier_id INT NULL;

-- 3. If courier_id doesn't have the foreign key constraint yet, add it
-- (Skip if it already exists from previous migration)
-- ALTER TABLE users 
-- ADD CONSTRAINT fk_rider_courier 
--     FOREIGN KEY (courier_id) REFERENCES users(id) ON DELETE SET NULL;

-- 4. Add index for faster queries (if not exists)
-- CREATE INDEX idx_users_courier ON users(courier_id);

-- Note: You may need to update existing data:
-- For couriers without company_name, you can set it to their full_name or email
-- UPDATE users SET company_name = full_name WHERE role = 'courier' AND company_name IS NULL;
