# Database Migration Instructions

## Error: Unknown column 'users.company_name' in 'field list'

This error occurs because the database schema hasn't been updated with the new columns required for the courier/rider separation feature.

## Solution

You have **3 options** to fix this:

### Option 1: Run the Python Migration Script (Recommended)

```bash
python3 apply_migrations.py
```

This script will:
- Check if columns already exist before adding them
- Handle renaming of `courier_company_id` to `courier_id`
- Add foreign key constraints and indexes
- Provide clear feedback on each step

### Option 2: Run the SQL Migration File

```bash
mysql -u root -p epicuremart < migration_unified_courier_rider.sql
```

This unified migration file handles all scenarios safely using conditional SQL.

### Option 3: Manual SQL Commands

If you prefer to run commands manually:

```sql
-- Connect to database
USE epicuremart;

-- Add company_name column
ALTER TABLE users 
ADD COLUMN company_name VARCHAR(200) NULL 
AFTER quick_reply_templates;

-- Option A: If you have courier_company_id, rename it
ALTER TABLE users 
CHANGE COLUMN courier_company_id courier_id INT NULL;

-- Option B: If you don't have either column, create courier_id
-- ALTER TABLE users 
-- ADD COLUMN courier_id INT NULL 
-- AFTER company_name;

-- Add foreign key constraint
ALTER TABLE users 
ADD CONSTRAINT fk_rider_courier 
FOREIGN KEY (courier_id) REFERENCES users(id) ON DELETE SET NULL;

-- Add index for performance
CREATE INDEX idx_users_courier ON users(courier_id);
```

## What These Columns Do

### `company_name` (VARCHAR 200)
- Stores courier company names (e.g., "J&T Express", "Lalamove", "NinjaVan")
- Only used for users with role = 'courier'
- NULL for other roles

### `courier_id` (INT, FK to users.id)
- Links riders to their courier company
- Only used for users with role = 'rider'
- References the courier user's ID
- NULL for other roles

## Verification

After running the migration, verify it worked:

```sql
-- Check if columns exist
SHOW COLUMNS FROM users LIKE 'company_name';
SHOW COLUMNS FROM users LIKE 'courier_id';

-- Check foreign key
SHOW CREATE TABLE users;
```

You should see both columns listed and the foreign key constraint.

## Complete Migration Order

If you're setting up from scratch, run these migrations in order:

1. `migration_rider_courier_visibility.sql` - Creates rider_feedback table
2. `migration_unified_courier_rider.sql` - Adds company_name and courier_id columns

OR just run:

```bash
python3 apply_migrations.py
```

This will handle everything automatically.

## Troubleshooting

### Error: "Duplicate column name 'company_name'"
The column already exists. You can skip adding it.

### Error: "Can't DROP 'courier_company_id'; check that column/key exists"
The old column doesn't exist. Create `courier_id` directly instead.

### Error: "Duplicate foreign key constraint name"
The constraint already exists. You can skip adding it.

### Still getting the error after migration?
1. Restart your Flask application
2. Clear any cached SQLAlchemy metadata
3. Verify columns exist: `SHOW COLUMNS FROM users;`

## Need Help?

If migrations fail, check:
1. MySQL is running: `sudo service mysql status`
2. Database exists: `SHOW DATABASES LIKE 'epicuremart';`
3. You have proper permissions: `SHOW GRANTS FOR CURRENT_USER();`
4. No syntax errors in migration file

For persistent issues, you can:
1. Backup your database: `mysqldump -u root -p epicuremart > backup.sql`
2. Drop and recreate: `DROP DATABASE epicuremart; CREATE DATABASE epicuremart;`
3. Run init_db.py to create tables
4. Run migrations
5. Restore data if needed
