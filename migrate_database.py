import pymysql

def migrate_database():
    print("=" * 60)
    print("   DATABASE MIGRATION - Add Commission Fields")
    print("=" * 60)
    
    # Connect to database
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Update if you have a password
        database='epicuremart'
    )
    
    try:
        cursor = connection.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'epicuremart' 
            AND TABLE_NAME = 'orders' 
            AND COLUMN_NAME = 'commission_rate'
        """)
        
        if cursor.fetchone():
            print("✅ Commission columns already exist!")
            return
        
        print("\n📝 Adding commission columns to orders table...")
        
        # Add commission_rate column
        cursor.execute("""
            ALTER TABLE orders 
            ADD COLUMN commission_rate DECIMAL(5,2) DEFAULT 5.00 
            AFTER total_amount
        """)
        print("✅ Added: commission_rate")
        
        # Add commission_amount column
        cursor.execute("""
            ALTER TABLE orders 
            ADD COLUMN commission_amount DECIMAL(10,2) DEFAULT 0.00 
            AFTER commission_rate
        """)
        print("✅ Added: commission_amount")
        
        # Add seller_amount column
        cursor.execute("""
            ALTER TABLE orders 
            ADD COLUMN seller_amount DECIMAL(10,2) DEFAULT 0.00 
            AFTER commission_amount
        """)
        print("✅ Added: seller_amount")
        
        connection.commit()
        
        # Update existing orders
        print("\n🔄 Updating existing orders with commission calculations...")
        cursor.execute("""
            UPDATE orders 
            SET commission_rate = 5.00,
                commission_amount = total_amount * 0.05,
                seller_amount = total_amount * 0.95
            WHERE commission_amount = 0
        """)
        
        affected_rows = cursor.rowcount
        connection.commit()
        
        print(f"✅ Updated {affected_rows} existing orders")
        
        print("\n" + "=" * 60)
        print("🎉 Migration completed successfully!")
        print("=" * 60)
        print("\n📊 New columns added:")
        print("   - commission_rate (5.00%)")
        print("   - commission_amount (auto-calculated)")
        print("   - seller_amount (95% of total)")
        print("\n✅ You can now restart your application!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    migrate_database()