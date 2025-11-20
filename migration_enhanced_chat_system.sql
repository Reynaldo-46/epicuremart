-- Migration: Enhanced Chat System with Images, Status, and Extended Types
-- Date: 2025-11-19

-- Update conversation_type enum to include user_admin and seller_courier
ALTER TABLE conversations 
MODIFY COLUMN conversation_type ENUM(
    'buyer_seller', 
    'seller_rider', 
    'buyer_rider', 
    'user_support', 
    'user_admin',
    'seller_courier'
) NOT NULL;

-- Add is_read_only flag for completed order conversations
ALTER TABLE conversations 
ADD COLUMN is_read_only BOOLEAN DEFAULT FALSE;

-- Add message status tracking fields to messages table
ALTER TABLE messages
ADD COLUMN message_type ENUM('text', 'image') DEFAULT 'text',
ADD COLUMN image_url VARCHAR(255) NULL,
ADD COLUMN status ENUM('sent', 'delivered', 'seen') DEFAULT 'sent',
ADD COLUMN delivered_at DATETIME NULL,
ADD COLUMN seen_at DATETIME NULL;

-- Add quick reply templates to users table (stored as JSON string)
ALTER TABLE users
ADD COLUMN quick_reply_templates TEXT NULL;

-- Create indexes for better query performance
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_type ON messages(message_type);
CREATE INDEX idx_conversations_readonly ON conversations(is_read_only);
CREATE INDEX idx_conversations_order ON conversations(order_id);
