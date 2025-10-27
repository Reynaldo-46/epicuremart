from app import app, db, User, Category, Shop, Product, DeliveryFee, Conversation, Message
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and seed data"""
    
    with app.app_context():
        print("🗄️  Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Create Admin User
        print("\n👤 Creating admin user...")
        admin = User.query.filter_by(email='admin@epicuremart.com').first()
        if not admin:
            admin = User(
                email='admin@epicuremart.com',
                role='admin',
                full_name='System Administrator',
                phone='+1234567890',
                is_verified=True,
                is_approved=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin created: admin@epicuremart.com / admin123")
        else:
            print("ℹ️  Admin already exists")
        
        # Create Categories
        print("\n📦 Creating categories...")
        categories_data = [
            {'name': 'Baking Supplies & Ingredients', 'icon': '🧁', 
             'description': 'Flour, sugar, baking powder, and all your baking needs'},
            {'name': 'Coffee, Tea & Beverages', 'icon': '☕', 
             'description': 'Premium coffee beans, tea leaves, and beverages'},
            {'name': 'Snacks & Candy', 'icon': '🍬', 
             'description': 'Delicious snacks, candies, and treats'},
            {'name': 'Specialty Foods & International Cuisines', 'icon': '🌍', 
             'description': 'Authentic international ingredients and specialty items'},
            {'name': 'Organic and Health Foods', 'icon': '🥗', 
             'description': 'Certified organic and health-conscious food options'},
            {'name': 'Meal Kits & Prepped Foods', 'icon': '🍱', 
             'description': 'Ready-to-cook meal kits and prepared foods'}
        ]
        
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(**cat_data)
                db.session.add(category)
                print(f"✅ Created: {cat_data['icon']} {cat_data['name']}")
            else:
                print(f"ℹ️  Already exists: {cat_data['name']}")
        
        db.session.commit()
        
        # Create Demo Seller (optional)
        print("\n🏪 Creating demo seller account...")
        demo_seller = User.query.filter_by(email='seller@demo.com').first()
        if not demo_seller:
            demo_seller = User(
                email='seller@demo.com',
                role='seller',
                full_name='Demo Seller',
                phone='+1234567891',
                is_verified=True,
                is_approved=True
            )
            demo_seller.set_password('seller123')
            db.session.add(demo_seller)
            db.session.flush()
            
            # Create demo shop
            demo_shop = Shop(
                seller_id=demo_seller.id,
                name='Artisan Bakery & Cafe',
                description='Premium baked goods and specialty coffee',
                is_active=True
            )
            db.session.add(demo_shop)
            db.session.flush()
            
            # Create sample products
            baking_cat = Category.query.filter_by(name='Baking Supplies & Ingredients').first()
            coffee_cat = Category.query.filter_by(name='Coffee, Tea & Beverages').first()
            
            sample_products = [
                {
                    'shop_id': demo_shop.id,
                    'category_id': baking_cat.id if baking_cat else 1,
                    'name': 'Organic All-Purpose Flour',
                    'description': 'Premium organic flour perfect for all baking needs',
                    'price': 8.99,
                    'stock': 50
                },
                {
                    'shop_id': demo_shop.id,
                    'category_id': coffee_cat.id if coffee_cat else 2,
                    'name': 'Premium Arabica Coffee Beans',
                    'description': 'Fresh roasted arabica beans from Colombia',
                    'price': 15.99,
                    'stock': 30
                },
                {
                    'shop_id': demo_shop.id,
                    'category_id': baking_cat.id if baking_cat else 1,
                    'name': 'Artisan Sourdough Starter',
                    'description': 'Live sourdough culture for homemade bread',
                    'price': 12.50,
                    'stock': 20
                }
            ]
            
            for prod_data in sample_products:
                product = Product(**prod_data)
                db.session.add(product)
            
            db.session.commit()
            print("✅ Demo seller created: seller@demo.com / seller123")
            print("✅ Demo shop 'Artisan Bakery & Cafe' created with 3 products")
        else:
            print("ℹ️  Demo seller already exists")
        
        # Create Demo Customer
        print("\n👥 Creating demo customer...")
        demo_customer = User.query.filter_by(email='customer@demo.com').first()
        if not demo_customer:
            demo_customer = User(
                email='customer@demo.com',
                role='customer',
                full_name='Demo Customer',
                phone='+1234567892',
                is_verified=True,
                is_approved=True
            )
            demo_customer.set_password('customer123')
            db.session.add(demo_customer)
            db.session.commit()
            print("✅ Demo customer created: customer@demo.com / customer123")
        else:
            print("ℹ️  Demo customer already exists")
        
        # Create Demo Courier
        print("\n🚚 Creating demo courier...")
        demo_courier = User.query.filter_by(email='courier@demo.com').first()
        if not demo_courier:
            demo_courier = User(
                email='courier@demo.com',
                role='courier',
                full_name='Demo Courier',
                phone='+1234567893',
                is_verified=True,
                is_approved=True
            )
            demo_courier.set_password('courier123')
            db.session.add(demo_courier)
            db.session.commit()
            print("✅ Demo courier created: courier@demo.com / courier123")
        else:
            print("ℹ️  Demo courier already exists")
        
        # Create Demo Rider
        print("\n🏍️  Creating demo rider...")
        demo_rider = User.query.filter_by(email='rider@demo.com').first()
        if not demo_rider:
            demo_rider = User(
                email='rider@demo.com',
                role='rider',
                full_name='Demo Rider',
                phone='+1234567894',
                is_verified=True,
                is_approved=True
            )
            demo_rider.set_password('rider123')
            db.session.add(demo_rider)
            db.session.commit()
            print("✅ Demo rider created: rider@demo.com / rider123")
        else:
            print("ℹ️  Demo rider already exists")
        
        print("\n" + "="*60)
        print("🎉 Database initialization complete!")
        print("="*60)
        print("\n📋 Demo Accounts:")
        print("   Admin:    admin@epicuremart.com / admin123")
        print("   Seller:   seller@demo.com / seller123")
        print("   Customer: customer@demo.com / customer123")
        print("   Courier:  courier@demo.com / courier123")
        print("   Rider:    rider@demo.com / rider123")
        print("\n🚀 Start the app with: python app.py")
        print("🌐 Then visit: http://localhost:5000")
        print("="*60)

if __name__ == '__main__':
    print("="*60)
    print("   EPICUREMART DATABASE INITIALIZATION")
    print("="*60)
    init_database()