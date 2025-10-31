-- Migration: Update conversations table for multi-party chat
-- Date: 2025-10-29

-- Rename columns
ALTER TABLE conversations 
CHANGE COLUMN customer_id user1_id INT NOT NULL,
CHANGE COLUMN seller_id user2_id INT NOT NULL;

-- Modify shop_id to be nullable
ALTER TABLE conversations 
MODIFY COLUMN shop_id INT NULL;

-- Add new columns
ALTER TABLE conversations
ADD COLUMN order_id INT NULL AFTER shop_id,
ADD COLUMN conversation_type ENUM('buyer_seller', 'seller_rider', 'buyer_rider') NOT NULL DEFAULT 'buyer_seller' AFTER order_id;

-- Add foreign key for order_id
ALTER TABLE conversations
ADD CONSTRAINT fk_conversation_order 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

-- Update existing records to have conversation_type
UPDATE conversations 
SET conversation_type = 'buyer_seller' 
WHERE conversation_type IS NULL OR conversation_type = '';
