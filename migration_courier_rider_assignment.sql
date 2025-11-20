-- Migration: Add Courier Company Assignment for Riders and Chat with Seller
-- Date: 2025-11-20

-- 1. Add courier_company_id field to users table for riders
ALTER TABLE users 
ADD COLUMN courier_company_id INT NULL AFTER quick_reply_templates,
ADD CONSTRAINT fk_rider_courier_company 
    FOREIGN KEY (courier_company_id) REFERENCES users(id) ON DELETE SET NULL;

-- 2. Add index for faster queries
CREATE INDEX idx_users_courier_company ON users(courier_company_id);
