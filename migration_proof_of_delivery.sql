-- Migration: Add proof of delivery field to orders table
-- Date: 2025-10-31

-- Add proof_of_delivery column to orders table
ALTER TABLE orders 
ADD COLUMN proof_of_delivery VARCHAR(255) NULL AFTER delivery_token;

-- Add comment
ALTER TABLE orders 
MODIFY COLUMN proof_of_delivery VARCHAR(255) NULL COMMENT 'Photo uploaded by rider as proof of delivery';
