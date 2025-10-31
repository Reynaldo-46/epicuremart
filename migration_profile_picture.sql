-- Migration: Add profile picture field to users table
-- Date: 2025-10-31

-- Add profile_picture column to users table
ALTER TABLE users 
ADD COLUMN profile_picture VARCHAR(255) NULL AFTER id_document;

-- Add comment
ALTER TABLE users 
MODIFY COLUMN profile_picture VARCHAR(255) NULL COMMENT 'Profile picture or business icon filename';
