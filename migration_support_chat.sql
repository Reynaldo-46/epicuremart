-- Migration for Support Chat System
-- Adds support agent functionality and extends conversation types

-- Add support agent flag to users table
ALTER TABLE users 
ADD COLUMN is_support_agent BOOLEAN DEFAULT FALSE,
ADD COLUMN last_activity DATETIME NULL;

-- Update conversation_type enum to include user_support
ALTER TABLE conversations 
MODIFY COLUMN conversation_type ENUM('buyer_seller', 'seller_rider', 'buyer_rider', 'user_support') NOT NULL;

-- Create index for faster support conversation queries
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_users_support_agent ON users(is_support_agent);
CREATE INDEX idx_messages_read ON messages(is_read);
