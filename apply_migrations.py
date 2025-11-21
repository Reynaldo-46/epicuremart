#!/usr/bin/env python3
"""
Apply database migrations for courier/rider visibility features
This script safely adds the necessary columns to the database
"""

from app import app, db
from sqlalchemy import text
import sys

def check_column_exists(column_name):
    """Check if a column exists in the users table"""
    try:
        result = db.session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = :column_name
        """), {"column_name": column_name})
        count = result.scalar()
        return count > 0
    except Exception as e:
        print(f"Error checking column {column_name}: {e}")
        return False

def add_company_name():
    """Add company_name column if it doesn't exist"""
    if check_column_exists('company_name'):
        print("✓ company_name column already exists")
        return True
    
    try:
        print("Adding company_name column...")
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN company_name VARCHAR(200) NULL 
            AFTER quick_reply_templates
        """))
        db.session.commit()
        print("✓ company_name column added successfully")
        return True
    except Exception as e:
        print(f"✗ Error adding company_name: {e}")
        db.session.rollback()
        return False

def handle_courier_id():
    """Handle courier_company_id -> courier_id migration"""
    has_old = check_column_exists('courier_company_id')
    has_new = check_column_exists('courier_id')
    
    if has_new:
        print("✓ courier_id column already exists")
        return True
    
    if has_old:
        # Rename courier_company_id to courier_id
        try:
            print("Renaming courier_company_id to courier_id...")
            db.session.execute(text("""
                ALTER TABLE users 
                CHANGE COLUMN courier_company_id courier_id INT NULL
            """))
            db.session.commit()
            print("✓ Column renamed successfully")
            return True
        except Exception as e:
            print(f"✗ Error renaming column: {e}")
            db.session.rollback()
            return False
    else:
        # Create courier_id column
        try:
            print("Adding courier_id column...")
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN courier_id INT NULL 
                AFTER company_name
            """))
            db.session.commit()
            print("✓ courier_id column added successfully")
            return True
        except Exception as e:
            print(f"✗ Error adding courier_id: {e}")
            db.session.rollback()
            return False

def add_foreign_key():
    """Add foreign key constraint if it doesn't exist"""
    try:
        # Check if FK exists
        result = db.session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND CONSTRAINT_NAME IN ('fk_rider_courier', 'fk_rider_courier_company')
        """))
        
        if result.scalar() > 0:
            print("✓ Foreign key constraint already exists")
            return True
        
        print("Adding foreign key constraint...")
        db.session.execute(text("""
            ALTER TABLE users 
            ADD CONSTRAINT fk_rider_courier 
            FOREIGN KEY (courier_id) REFERENCES users(id) ON DELETE SET NULL
        """))
        db.session.commit()
        print("✓ Foreign key constraint added successfully")
        return True
    except Exception as e:
        print(f"✗ Error adding foreign key: {e}")
        db.session.rollback()
        return False

def add_index():
    """Add index if it doesn't exist"""
    try:
        # Check if index exists
        result = db.session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND INDEX_NAME IN ('idx_users_courier', 'idx_users_courier_company')
        """))
        
        if result.scalar() > 0:
            print("✓ Index already exists")
            return True
        
        print("Adding index...")
        db.session.execute(text("""
            CREATE INDEX idx_users_courier ON users(courier_id)
        """))
        db.session.commit()
        print("✓ Index added successfully")
        return True
    except Exception as e:
        print(f"✗ Error adding index: {e}")
        db.session.rollback()
        return False

def add_courier_profile_fields():
    """Add courier profile fields (company_logo, company_address, company_description)"""
    fields = [
        ('company_logo', 'VARCHAR(255)', 'AFTER company_name'),
        ('company_address', 'TEXT', 'AFTER company_logo'),
        ('company_description', 'TEXT', 'AFTER company_address'),
    ]
    
    for field_name, field_type, position in fields:
        if check_column_exists(field_name):
            print(f"✓ {field_name} column already exists")
            continue
        
        try:
            print(f"Adding {field_name} column...")
            db.session.execute(text(f"""
                ALTER TABLE users 
                ADD COLUMN {field_name} {field_type} NULL {position}
            """))
            db.session.commit()
            print(f"✓ {field_name} column added successfully")
        except Exception as e:
            print(f"✗ Error adding {field_name}: {e}")
            db.session.rollback()
            return False
    
    return True

def main():
    """Run all migrations"""
    print("=" * 60)
    print("Database Migration: Courier/Rider Visibility Features")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text("SELECT 1"))
            print("✓ Database connection successful\n")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            sys.exit(1)
        
        # Run migrations in order
        steps = [
            ("Add company_name column", add_company_name),
            ("Handle courier_id column", handle_courier_id),
            ("Add foreign key constraint", add_foreign_key),
            ("Add index", add_index),
            ("Add courier profile fields", add_courier_profile_fields),
        ]
        
        failed = False
        for step_name, step_func in steps:
            print(f"\nStep: {step_name}")
            print("-" * 60)
            if not step_func():
                failed = True
                print(f"✗ Failed: {step_name}")
                break
        
        if not failed:
            print("\n" + "=" * 60)
            print("✓ All migrations completed successfully!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("✗ Migration failed. Please check the errors above.")
            print("=" * 60)
            sys.exit(1)

if __name__ == '__main__':
    main()
