-- Comprehensive Migration for EpicureMart System Improvements
-- This migration adds all required schema changes for the new features

-- 1. Add CartItem table for transaction-based cart
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Add verification code field to users table (for email verification)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS verification_code VARCHAR(10) DEFAULT NULL AFTER is_verified,
ADD COLUMN IF NOT EXISTS verification_code_expires DATETIME DEFAULT NULL AFTER verification_code;

-- 3. Add seller verification documents
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS business_permit VARCHAR(255) DEFAULT NULL AFTER id_document;

-- 4. Add rider/courier verification fields
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS drivers_license VARCHAR(255) DEFAULT NULL AFTER business_permit,
ADD COLUMN IF NOT EXISTS or_cr VARCHAR(255) DEFAULT NULL AFTER drivers_license,
ADD COLUMN IF NOT EXISTS plate_number VARCHAR(50) DEFAULT NULL AFTER or_cr,
ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(50) DEFAULT NULL AFTER plate_number;

-- 5. Add suspension/status fields
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_suspended BOOLEAN DEFAULT FALSE AFTER is_approved,
ADD COLUMN IF NOT EXISTS suspension_reason TEXT DEFAULT NULL AFTER is_suspended;

-- 6. Add additional address fields
ALTER TABLE addresses 
ADD COLUMN IF NOT EXISTS street VARCHAR(255) DEFAULT NULL AFTER barangay,
ADD COLUMN IF NOT EXISTS block VARCHAR(50) DEFAULT NULL AFTER street,
ADD COLUMN IF NOT EXISTS lot VARCHAR(50) DEFAULT NULL AFTER block;

-- 7. Add courier/rider earnings tracking to orders
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS courier_earnings DECIMAL(10, 2) DEFAULT 0.00 AFTER seller_amount,
ADD COLUMN IF NOT EXISTS rider_earnings DECIMAL(10, 2) DEFAULT 0.00 AFTER courier_earnings,
ADD COLUMN IF NOT EXISTS shipping_fee_split_courier DECIMAL(5, 2) DEFAULT 60.00 AFTER rider_earnings,
ADD COLUMN IF NOT EXISTS shipping_fee_split_rider DECIMAL(5, 2) DEFAULT 40.00 AFTER shipping_fee_split_courier;

-- 8. Add message read tracking for better notification badges
-- Already exists as is_read in messages table

-- 9. Create index for faster unread message queries
CREATE INDEX IF NOT EXISTS idx_messages_unread ON messages(sender_id, is_read);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, is_read);

-- 10. Update conversations table to support admin support chats
ALTER TABLE conversations 
MODIFY COLUMN conversation_type ENUM('buyer_seller', 'seller_rider', 'buyer_rider', 'user_support', 'user_admin') NOT NULL;
