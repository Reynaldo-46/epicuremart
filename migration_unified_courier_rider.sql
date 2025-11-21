-- Combined Migration: Add all courier/rider visibility features
-- This migration handles all scenarios and can be run safely
-- Date: 2025-11-20

-- Check and add columns safely
SET @dbname = DATABASE();
SET @tablename = 'users';

-- Add company_name if it doesn't exist
SET @col_exists = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'company_name');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN company_name VARCHAR(200) NULL AFTER quick_reply_templates',
    'SELECT "Column company_name already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Handle courier_company_id / courier_id
-- First check if courier_company_id exists
SET @col_exists_old = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'courier_company_id');

-- Check if courier_id exists
SET @col_exists_new = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'courier_id');

-- If courier_company_id exists but courier_id doesn't, rename it
SET @sql = IF(@col_exists_old = 1 AND @col_exists_new = 0,
    'ALTER TABLE users CHANGE COLUMN courier_company_id courier_id INT NULL',
    'SELECT "Skipping courier_company_id rename" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- If neither exists, create courier_id
SET @col_exists_new = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'courier_id');

SET @sql = IF(@col_exists_new = 0,
    'ALTER TABLE users ADD COLUMN courier_id INT NULL AFTER company_name',
    'SELECT "Column courier_id already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add foreign key constraint if it doesn't exist
SET @fk_exists = (SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = @dbname
    AND TABLE_NAME = @tablename
    AND CONSTRAINT_NAME IN ('fk_rider_courier', 'fk_rider_courier_company')
    AND COLUMN_NAME IN ('courier_id', 'courier_company_id'));

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE users ADD CONSTRAINT fk_rider_courier FOREIGN KEY (courier_id) REFERENCES users(id) ON DELETE SET NULL',
    'SELECT "Foreign key constraint already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add index if it doesn't exist
SET @idx_exists = (SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = @dbname
    AND TABLE_NAME = @tablename
    AND INDEX_NAME IN ('idx_users_courier', 'idx_users_courier_company'));

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX idx_users_courier ON users(courier_id)',
    'SELECT "Index already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Migration completed successfully' AS status;
