-- Migration: Add Courier Company Logo and Additional Fields
-- Date: 2025-11-21

-- Add company_logo field for courier companies
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS company_logo VARCHAR(255) NULL AFTER company_name;

-- Add company_address field for courier companies
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS company_address TEXT NULL AFTER company_logo;

-- Add company_description field for courier companies
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS company_description TEXT NULL AFTER company_address;

-- For MySQL versions that don't support IF NOT EXISTS, use this alternative:
-- Check and add columns if they don't exist

SET @dbname = DATABASE();
SET @tablename = 'users';

-- Add company_logo if it doesn't exist
SET @col_exists = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'company_logo');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN company_logo VARCHAR(255) NULL AFTER company_name',
    'SELECT "Column company_logo already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add company_address if it doesn't exist
SET @col_exists = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'company_address');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN company_address TEXT NULL AFTER company_logo',
    'SELECT "Column company_address already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add company_description if it doesn't exist
SET @col_exists = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'company_description');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN company_description TEXT NULL AFTER company_address',
    'SELECT "Column company_description already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Migration completed successfully' AS status;
