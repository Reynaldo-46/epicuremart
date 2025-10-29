"""
Run Database Migrations for Epicuremart Enhancements
This script applies all pending migrations to the database.
"""

import pymysql
import os

def run_migrations():
    """Apply all SQL migration files"""
    
    # Database connection
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='epicuremart'
    )
    
    try:
        cursor = connection.cursor()
        
        # Migration files in order
        migrations = [
            'migration_registration_updates.sql',
            'migration_chat_updates.sql'
        ]
        
        print("="*60)
        print("   EPICUREMART DATABASE MIGRATIONS")
        print("="*60)
        
        for migration_file in migrations:
            if not os.path.exists(migration_file):
                print(f"\n⚠️  Warning: {migration_file} not found, skipping...")
                continue
                
            print(f"\n📝 Running migration: {migration_file}")
            
            with open(migration_file, 'r') as f:
                sql_commands = f.read()
                
                # Split by semicolon and execute each command
                for command in sql_commands.split(';'):
                    command = command.strip()
                    if command and not command.startswith('--'):
                        try:
                            cursor.execute(command)
                            connection.commit()
                        except Exception as e:
                            # Some errors are expected (like column already exists)
                            if "Duplicate column name" in str(e) or "already exists" in str(e):
                                print(f"   ℹ️  Skipping (already applied): {command[:50]}...")
                            else:
                                print(f"   ⚠️  Error: {e}")
            
            print(f"✅ Completed: {migration_file}")
        
        print("\n" + "="*60)
        print("🎉 All migrations completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running migrations: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    print("\n⚠️  WARNING: This will modify your database structure!")
    print("   Make sure you have a backup before proceeding.")
    
    response = input("\nContinue with migrations? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        run_migrations()
    else:
        print("❌ Migrations cancelled.")
