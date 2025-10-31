"""
Run Database Migrations for Epicuremart Enhancements
This script applies all pending migrations to the database.
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migrations():
    """Apply all SQL migration files"""
    
    # Database connection using environment variables
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'epicuremart')
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
            
            try:
                with open(migration_file, 'r') as f:
                    sql_commands = f.read()
                    
                    # Split by semicolon and execute each command
                    for command in sql_commands.split(';'):
                        command = command.strip()
                        if command and not command.startswith('--'):
                            try:
                                cursor.execute(command)
                            except pymysql.err.OperationalError as e:
                                error_code = e.args[0]
                                # 1060 = Duplicate column name, 1061 = Duplicate key name
                                if error_code in [1060, 1061]:
                                    print(f"   ℹ️  Skipping (already applied): {command[:50]}...")
                                else:
                                    raise
                            except Exception as e:
                                print(f"   ⚠️  Error in command: {e}")
                                raise
                
                # Commit all changes for this migration file
                connection.commit()
                print(f"✅ Completed: {migration_file}")
                
            except Exception as e:
                print(f"   ❌ Failed: {migration_file} - {e}")
                connection.rollback()
                raise
        
        print("\n" + "="*60)
        print("🎉 All migrations completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running migrations: {e}")
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
