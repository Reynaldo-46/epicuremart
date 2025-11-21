-- Migration: Add Rider Lock Mechanism
-- Date: 2025-11-21

-- Add rider_locked field to orders table to prevent reassignment after handoff
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS rider_locked BOOLEAN DEFAULT FALSE AFTER delivery_token;

-- For MySQL versions that don't support IF NOT EXISTS:
SET @dbname = DATABASE();
SET @tablename = 'orders';

-- Add rider_locked if it doesn't exist
SET @col_exists = (SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'rider_locked');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE orders ADD COLUMN rider_locked BOOLEAN DEFAULT FALSE AFTER delivery_token',
    'SELECT "Column rider_locked already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Set default value to FALSE for existing records
UPDATE orders SET rider_locked = FALSE WHERE rider_locked IS NULL;

SELECT 'Migration completed successfully - Rider lock mechanism added' AS status;
