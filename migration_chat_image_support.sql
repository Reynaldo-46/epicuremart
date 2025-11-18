-- Migration to add image support to messages
-- This adds an image column to the messages table and makes message_text nullable

-- Add image column for uploaded images
ALTER TABLE messages ADD COLUMN image VARCHAR(255) DEFAULT NULL;

-- Make message_text nullable to allow image-only messages
ALTER TABLE messages MODIFY COLUMN message_text TEXT NULL;
