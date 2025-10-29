from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
import jwt
import qrcode
import io
import base64
import os
import secrets
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import Numeric


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/epicuremart'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'reynaldo.yasona06@gmail.com'
app.config['MAIL_PASSWORD'] = 'urantilhbyppxpqe'
app.config['MAIL_DEFAULT_SENDER'] = 'Epicuremart <noreply@epicuremart.com>'

db = SQLAlchemy(app)
mail = Mail(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ==================== MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'seller', 'customer', 'courier', 'rider'), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)  # Admin approval for sellers/couriers/riders
    full_name = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    id_document = db.Column(db.String(255))  # File path for uploaded ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shop = db.relationship('Shop', backref='owner', uselist=False, cascade='all, delete-orphan')
    addresses = db.relationship('Address', backref='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', foreign_keys='Order.customer_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    logo = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    products = db.relationship('Product', backref='shop', cascade='all, delete-orphan')


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    products = db.relationship('Product', backref='category')




class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(Numeric(10, 2), nullable=False)  # ✅ FIXED
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label = db.Column(db.String(50))  # Home, Work, etc.
    full_address = db.Column(db.Text, nullable=False)
    region = db.Column(db.String(100))
    province = db.Column(db.String(100))
    municipality = db.Column(db.String(100))
    city = db.Column(db.String(100))
    barangay = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    courier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rider_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    status = db.Column(db.Enum(
        'PENDING_PAYMENT', 'READY_FOR_PICKUP', 'IN_TRANSIT_TO_RIDER',
        'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED'
    ), default='PENDING_PAYMENT')
    
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    delivery_fee = db.Column(Numeric(10, 2), default=0.00)
    subtotal = db.Column(Numeric(10, 2), nullable=False)
    commission_rate = db.Column(Numeric(5, 2), default=5.00)  # 5% commission
    commission_amount = db.Column(Numeric(10, 2), default=0.00)
    seller_amount = db.Column(Numeric(10, 2), default=0.00)

    # QR Tokens
    pickup_token = db.Column(db.String(500))  # JWT for courier pickup
    delivery_token = db.Column(db.String(500))  # JWT for customer delivery
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    delivery_address = db.relationship('Address', foreign_keys=[delivery_address_id])
    shop = db.relationship('Shop', foreign_keys=[shop_id])
    courier = db.relationship('User', foreign_keys=[courier_id])
    rider = db.relationship('User', foreign_keys=[rider_id])


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    
    product = db.relationship('Product')

class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    review_images = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='reviews')
    user = db.relationship('User')
    order = db.relationship('Order')


class DeliveryFee(db.Model):
    __tablename__ = 'delivery_fees'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False, unique=True)
    province = db.Column(db.String(50), nullable=False)
    fee = db.Column(Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User')

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))  # Optional, for buyer-seller conversations
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))  # Optional, for order-related conversations
    conversation_type = db.Column(db.Enum('buyer_seller', 'seller_rider', 'buyer_rider'), nullable=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    shop = db.relationship('Shop', foreign_keys=[shop_id])
    order = db.relationship('Order', foreign_keys=[order_id])
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan', order_by='Message.created_at')


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User')
    
# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            
            if not user.is_approved and user.role in ['seller', 'courier', 'rider']:
                flash('Your account is pending approval.', 'warning')
                return redirect(url_for('pending_approval'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_action(action, entity_type=None, entity_id=None, details=None):
    """Create audit log entry"""
    try:
        log = AuditLog(
            user_id=session.get('user_id'),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Logging error: {e}")


def send_email(to, subject, body):
    """Send email notification"""
    try:
        msg = Message(subject, recipients=[to])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def generate_qr_token(order_id, token_type, expiry_hours=24):
    """Generate JWT token for QR code"""
    payload = {
        'order_id': order_id,
        'type': token_type,  # 'pickup' or 'delivery'
        'exp': datetime.utcnow() + timedelta(hours=expiry_hours)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def verify_qr_token(token):
    """Verify and decode JWT token from QR"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_qr_code(data):
    """Generate QR code image as base64"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()


def generate_order_number():
    """Generate unique order number"""
    import random
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"EM{timestamp}{random_part}"


# ==================== ROUTES ====================

@app.route('/')
def index():
    categories = Category.query.all()
    products = Product.query.filter_by(is_active=True).limit(12).all()
    # conversation = Conversation.query.all()
    return render_template('index.html', categories=categories, products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'customer')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name', '')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Address fields
        region = request.form.get('region')
        province = request.form.get('province')
        municipality = request.form.get('municipality')
        city = request.form.get('city')
        barangay = request.form.get('barangay')
        
        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        # Sellers, couriers, riders need admin approval
        is_approved = True if role == 'customer' else False
        
        # Construct full name
        full_name = f"{first_name} {middle_name} {last_name}".replace('  ', ' ').strip()
        
        user = User(
            email=email,
            role=role,
            full_name=full_name,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            phone=phone,
            is_approved=is_approved
        )
        user.set_password(password)
        
        # Handle ID document upload for sellers, couriers, riders
        if role in ['seller', 'courier', 'rider']:
            if 'id_document' in request.files:
                file = request.files['id_document']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"id_{role}_{email.split('@')[0]}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    user.id_document = filename
                else:
                    flash('Valid ID document is required for this role.', 'danger')
                    return redirect(url_for('register'))
            else:
                flash('ID document upload is required for sellers, couriers, and riders.', 'danger')
                return redirect(url_for('register'))
        
        db.session.add(user)
        db.session.commit()
        
        # Create address entry if provided
        if region and province and barangay:
            full_address = f"{barangay}, {city or municipality}, {province}, {region}"
            address = Address(
                user_id=user.id,
                label='Home',
                full_address=full_address,
                region=region,
                province=province,
                municipality=municipality,
                city=city,
                barangay=barangay,
                is_default=True
            )
            db.session.add(address)
            db.session.commit()
        
        # Send verification email
        verification_token = generate_qr_token(user.id, 'email_verify', expiry_hours=48)
        verify_url = url_for('verify_email', token=verification_token, _external=True)
        send_email(
            user.email,
            'Verify your Epicuremart account',
            f'Click here to verify: {verify_url}'
        )
        
        log_action('USER_REGISTERED', 'User', user.id, f'New {role} registered')
        
        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/verify-email/<token>')
def verify_email(token):
    payload = verify_qr_token(token)
    if not payload or payload.get('type') != 'email_verify':
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get(payload['order_id'])  # Reusing order_id field for user_id
    if user:
        user.is_verified = True
        db.session.commit()
        log_action('EMAIL_VERIFIED', 'User', user.id)
        flash('Email verified successfully! You can now log in.', 'success')
    
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['role'] = user.role
            
            log_action('USER_LOGIN', 'User', user.id)
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'seller':
                if not user.is_approved:
                    return redirect(url_for('pending_approval'))
                return redirect(url_for('seller_dashboard'))
            elif user.role == 'courier':
                if not user.is_approved:
                    return redirect(url_for('pending_approval'))
                return redirect(url_for('courier_dashboard'))
            elif user.role == 'rider':
                if not user.is_approved:
                    return redirect(url_for('pending_approval'))
                return redirect(url_for('rider_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    log_action('USER_LOGOUT', 'User', session.get('user_id'))
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/pending-approval')
@login_required
def pending_approval():
    return render_template('pending_approval.html')


# ==================== CUSTOMER ROUTES ====================

@app.route('/browse')
def browse():
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Product.name.like(f'%{search}%'))
    
    products = query.all()
    categories = Category.query.all()
    
    return render_template('browse.html', products=products, categories=categories)


@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = float(product.price) * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    cart = session.get('cart', {})
    
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    
    session['cart'] = cart
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('browse'))


@app.route('/cart/remove/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        flash('Item removed from cart.', 'info')
    return redirect(url_for('view_cart'))

@app.route('/customer/address/add', methods=['POST'])
@login_required
@role_required('customer')
def add_address():
    label = request.form.get('label')
    full_address = request.form.get('full_address')
    city = request.form.get('city')
    postal_code = request.form.get('postal_code')
    is_default = request.form.get('is_default') == '1'
    redirect_to = request.form.get('redirect_to', 'checkout')
    
    # If this is set as default, unset other defaults
    if is_default:
        Address.query.filter_by(user_id=session['user_id'], is_default=True).update({'is_default': False})
    
    # If this is the first address, make it default
    if Address.query.filter_by(user_id=session['user_id']).count() == 0:
        is_default = True
    
    address = Address(
        user_id=session['user_id'],
        label=label,
        full_address=full_address,
        city=city,
        postal_code=postal_code,
        is_default=is_default
    )
    
    db.session.add(address)
    db.session.commit()
    
    log_action('ADDRESS_ADDED', 'Address', address.id, f'Added {label} address')
    flash('Delivery address added successfully!', 'success')
    
    if redirect_to == 'profile':
        return redirect(url_for('customer_profile'))
    return redirect(url_for('checkout'))


@app.route('/customer/profile')
@login_required
@role_required('customer')
def customer_profile():
    user = User.query.get(session['user_id'])
    addresses = Address.query.filter_by(user_id=session['user_id']).all()
    return render_template('customer_profile.html', current_user=user, addresses=addresses)


@app.route('/customer/address/<int:address_id>/set-default', methods=['POST'])
@login_required
@role_required('customer')
def set_default_address(address_id):
    # Unset all defaults
    Address.query.filter_by(user_id=session['user_id']).update({'is_default': False})
    
    # Set new default
    address = Address.query.get_or_404(address_id)
    if address.user_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('customer_profile'))
    
    address.is_default = True
    db.session.commit()
    
    log_action('ADDRESS_SET_DEFAULT', 'Address', address.id)
    flash(f'{address.label} address set as default.', 'success')
    return redirect(url_for('customer_profile'))


@app.route('/customer/address/<int:address_id>/delete', methods=['POST'])
@login_required
@role_required('customer')
def delete_address(address_id):
    address = Address.query.get_or_404(address_id)
    
    if address.user_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('customer_profile'))
    
    was_default = address.is_default
    label = address.label
    
    db.session.delete(address)
    
    # If deleted address was default, set another as default
    if was_default:
        new_default = Address.query.filter_by(user_id=session['user_id']).first()
        if new_default:
            new_default.is_default = True
    
    db.session.commit()
    
    log_action('ADDRESS_DELETED', 'Address', address_id, f'Deleted {label} address')
    flash('Address deleted successfully.', 'success')
    return redirect(url_for('customer_profile'))




@app.route('/checkout', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('browse'))
    
    addresses = Address.query.filter_by(user_id=session['user_id']).all()
    
    if request.method == 'POST':
        address_id = request.form.get('address_id')
        
        # Group items by shop
        shop_orders = {}
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                if product.shop_id not in shop_orders:
                    shop_orders[product.shop_id] = []
                shop_orders[product.shop_id].append((product, quantity))
        
        # Create order for each shop
        for shop_id, items in shop_orders.items():
            total = sum([float(p.price) * q for p, q in items])
            
            commission = total * 0.05
            seller_amount = total - commission
            
            order = Order(
                order_number=generate_order_number(),
                customer_id=session['user_id'],
                shop_id=shop_id,
                delivery_address_id=address_id,
                total_amount=total,
                commission_rate=5.00,
                commission_amount=commission,
                seller_amount=seller_amount,
                status='PENDING_PAYMENT'
            )
            db.session.add(order)
            db.session.flush()
            
            for product, quantity in items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=product.price
                )
                db.session.add(order_item)
            
            log_action('ORDER_CREATED', 'Order', order.id, f'Order {order.order_number}')
        
        db.session.commit()
        session['cart'] = {}
        
        # Send confirmation email
        user = User.query.get(session['user_id'])
        send_email(
            user.email,
            'Order Confirmation',
            f'Your orders have been placed successfully!'
        )
        
        flash('Order(s) placed successfully!', 'success')
        return redirect(url_for('customer_orders'))
    
    return render_template('checkout.html', addresses=addresses)


@app.route('/customer/orders')
@login_required
@role_required('customer')
def customer_orders():
    orders = Order.query.filter_by(customer_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('customer_orders.html', orders=orders)


@app.route('/customer/order/<int:order_id>')
@login_required
@role_required('customer')
def customer_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.customer_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('customer_orders'))
    
    # Generate QR code for delivery confirmation
    qr_data = None
    if order.delivery_token:
        qr_data = generate_qr_code(order.delivery_token)
    
    # Check which products can be reviewed
    reviewable_items = []
    if order.status == 'DELIVERED':
        for item in order.items:
            existing_review = ProductReview.query.filter_by(
                product_id=item.product_id,
                user_id=session['user_id'],
                order_id=order.id
            ).first()
            reviewable_items.append({
                'item': item,
                'has_review': existing_review is not None,
                'review': existing_review
            })
    
    return render_template('customer_order_detail.html', 
        order=order, 
        qr_data=qr_data,
        reviewable_items=reviewable_items
    )


@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
@role_required('customer')
def add_product_review(product_id):
    order_id = request.form.get('order_id')
    rating = request.form.get('rating')
    review_text = request.form.get('review_text')
    
    # Verify customer bought this product in this order
    order = Order.query.get_or_404(order_id)
    if order.customer_id != session['user_id'] or order.status != 'DELIVERED':
        flash('You can only review products from delivered orders.', 'danger')
        return redirect(url_for('customer_order_detail', order_id=order_id))
    
    # Check if already reviewed
    existing = ProductReview.query.filter_by(
        product_id=product_id,
        user_id=session['user_id'],
        order_id=order_id
    ).first()
    
    if existing:
        flash('You have already reviewed this product.', 'warning')
        return redirect(url_for('customer_order_detail', order_id=order_id))
    
    uploaded_images = []
    for i in range(1, 6):  # Support up to 5 images
        image_key = f'review_image_{i}'
        if image_key in request.files:
            file = request.files[image_key]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"review_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_images.append(filename)
    
    review = ProductReview(
        product_id=product_id,
        user_id=session['user_id'],
        order_id=order_id,
        rating=int(rating),
        review_text=review_text,
        review_images=",".join(uploaded_images)
    )
    
    db.session.add(review)
    db.session.commit()
    
    log_action('PRODUCT_REVIEWED', 'ProductReview', review.id, f'{rating} stars')
    flash('Thank you for your review!', 'success')
    return redirect(url_for('customer_order_detail', order_id=order_id))


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Calculate average rating
    reviews = ProductReview.query.filter_by(product_id=product_id).all()
    avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_counts[review.rating] += 1
    
    return render_template('product_detail.html',
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        rating_counts=rating_counts,
        total_reviews=len(reviews)
    )



# @app.route('/customer/order/<int:order_id>')
# @login_required
# @role_required('customer')
# def customer_order_detail(order_id):
#     order = Order.query.get_or_404(order_id)
    
#     if order.customer_id != session['user_id']:
#         flash('Unauthorized access.', 'danger')
#         return redirect(url_for('customer_orders'))
    
#     # Generate QR code for delivery confirmation
#     qr_data = None
#     if order.delivery_token:
#         qr_data = generate_qr_code(order.delivery_token)
    
#     return render_template('customer_order_detail.html', order=order, qr_data=qr_data)


# ==================== SELLER ROUTES ====================

@app.route('/seller/dashboard')
@login_required
@role_required('seller')
def seller_dashboard():
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    user = User.query.get(session['user_id'])
    
    if not user.shop:
        return redirect(url_for('create_shop'))
    
    # Get filter parameter
    time_filter = request.args.get('filter', 'all')
    
    # Calculate date range based on filter
    now = datetime.utcnow()
    if time_filter == 'day':
        start_date = now - timedelta(days=1)
    elif time_filter == 'week':
        start_date = now - timedelta(weeks=1)
    elif time_filter == 'month':
        start_date = now - timedelta(days=30)
    elif time_filter == 'year':
        start_date = now - timedelta(days=365)
    else:
        start_date = None
    
    # Statistics
    total_products = Product.query.filter_by(shop_id=user.shop.id).count()
    total_orders = Order.query.filter_by(shop_id=user.shop.id).count()
    pending_orders = Order.query.filter_by(
        shop_id=user.shop.id, 
        status='PENDING_PAYMENT'
    ).count()
    ready_orders = Order.query.filter_by(
        shop_id=user.shop.id, 
        status='READY_FOR_PICKUP'
    ).count()
    
    # Revenue calculations
    revenue_query = db.session.query(func.sum(Order.seller_amount))\
        .filter(Order.shop_id == user.shop.id, Order.status == 'DELIVERED')
    if start_date:
        revenue_query = revenue_query.filter(Order.created_at >= start_date)
    total_revenue = revenue_query.scalar() or 0
    
    # Total sales (before commission)
    sales_query = db.session.query(func.sum(Order.subtotal))\
        .filter(Order.shop_id == user.shop.id, Order.status == 'DELIVERED')
    if start_date:
        sales_query = sales_query.filter(Order.created_at >= start_date)
    total_sales = sales_query.scalar() or 0
    
    # Average order value
    avg_order_query = db.session.query(func.avg(Order.total_amount))\
        .filter(Order.shop_id == user.shop.id, Order.status == 'DELIVERED')
    if start_date:
        avg_order_query = avg_order_query.filter(Order.created_at >= start_date)
    avg_order_value = avg_order_query.scalar() or 0
    
    # Revenue data for chart
    revenue_chart_data = []
    if time_filter == 'day' or time_filter == 'week':
        # Daily data for last 7 days
        for i in range(6, -1, -1):
            date = now - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            daily_revenue = db.session.query(func.sum(Order.seller_amount))\
                .filter(Order.shop_id == user.shop.id,
                        Order.created_at >= day_start, 
                        Order.created_at < day_end,
                        Order.status == 'DELIVERED').scalar() or 0
            
            revenue_chart_data.append({
                'label': day_start.strftime('%b %d'),
                'value': float(daily_revenue)
            })
    elif time_filter == 'month':
        # Weekly data for last 4 weeks
        for i in range(3, -1, -1):
            week_start = now - timedelta(weeks=i+1)
            week_end = now - timedelta(weeks=i)
            
            weekly_revenue = db.session.query(func.sum(Order.seller_amount))\
                .filter(Order.shop_id == user.shop.id,
                        Order.created_at >= week_start, 
                        Order.created_at < week_end,
                        Order.status == 'DELIVERED').scalar() or 0
            
            revenue_chart_data.append({
                'label': f'Week {i+1}',
                'value': float(weekly_revenue)
            })
    else:
        # Monthly data for last 12 months
        for i in range(11, -1, -1):
            month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = now
            else:
                month_end = (now - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_revenue = db.session.query(func.sum(Order.seller_amount))\
                .filter(Order.shop_id == user.shop.id,
                        Order.created_at >= month_start, 
                        Order.created_at < month_end,
                        Order.status == 'DELIVERED').scalar() or 0
            
            revenue_chart_data.append({
                'label': month_start.strftime('%b %Y'),
                'value': float(monthly_revenue)
            })
    
    # Top selling products
    top_products = db.session.query(
        Product.name, 
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).join(Order)\
        .filter(Product.shop_id == user.shop.id, Order.status == 'DELIVERED')\
        .group_by(Product.id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
    
    recent_orders = Order.query.filter_by(shop_id=user.shop.id)\
        .order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('seller_dashboard.html',
        shop=user.shop,
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        ready_orders=ready_orders,
        total_revenue=total_revenue,
        total_sales=total_sales,
        avg_order_value=avg_order_value,
        revenue_chart_data=revenue_chart_data,
        top_products=top_products,
        time_filter=time_filter,
        recent_orders=recent_orders
    )


@app.route('/seller/shop/create', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def create_shop():
    user = User.query.get(session['user_id'])
    
    if user.shop:
        flash('You already have a shop.', 'info')
        return redirect(url_for('seller_dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        logo = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"shop_{user.id}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                logo = filename
        
        shop = Shop(
            seller_id=user.id,
            name=name,
            description=description,
            logo=logo
        )
        db.session.add(shop)
        db.session.commit()
        
        log_action('SHOP_CREATED', 'Shop', shop.id, f'Shop: {name}')
        flash('Shop created successfully!', 'success')
        return redirect(url_for('seller_dashboard'))
    
    return render_template('create_shop.html')


@app.route('/seller/products')
@login_required
@role_required('seller')
def seller_products():
    user = User.query.get(session['user_id'])
    products = Product.query.filter_by(shop_id=user.shop.id).all()
    return render_template('seller_products.html', products=products)


@app.route('/seller/product/create', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def create_product():
    user = User.query.get(session['user_id'])
    categories = Category.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category_id = request.form.get('category_id')
        
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"product_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image = filename
        
        product = Product(
            shop_id=user.shop.id,
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image
        )
        db.session.add(product)
        db.session.commit()
        
        log_action('PRODUCT_CREATED', 'Product', product.id, f'Product: {name}')
        flash('Product created successfully!', 'success')
        return redirect(url_for('seller_products'))
    
    return render_template('create_product.html', categories=categories)


@app.route('/seller/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def edit_product(product_id):
    user = User.query.get(session['user_id'])
    product = Product.query.get_or_404(product_id)
    
    if product.shop_id != user.shop.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('seller_products'))
    
    categories = Category.query.all()
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price')
        product.stock = request.form.get('stock')
        product.category_id = request.form.get('category_id')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"product_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                product.image = filename
        
        db.session.commit()
        
        log_action('PRODUCT_UPDATED', 'Product', product.id, f'Updated: {product.name}')
        flash('Product updated successfully!', 'success')
        return redirect(url_for('seller_products'))
    
    return render_template('edit_product.html', product=product, categories=categories)


@app.route('/seller/product/<int:product_id>/delete', methods=['POST'])
@login_required
@role_required('seller')
def delete_product(product_id):
    user = User.query.get(session['user_id'])
    product = Product.query.get_or_404(product_id)
    
    if product.shop_id != user.shop.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('seller_products'))
    
    log_action('PRODUCT_DELETED', 'Product', product.id, f'Deleted: {product.name}')
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('seller_products'))


@app.route('/seller/orders')
@login_required
@role_required('seller')
def seller_orders():
    user = User.query.get(session['user_id'])
    orders = Order.query.filter_by(shop_id=user.shop.id)\
        .order_by(Order.created_at.desc()).all()
    return render_template('seller_orders.html', orders=orders)


@app.route('/seller/order/<int:order_id>')
@login_required
@role_required('seller')
def seller_order_detail(order_id):
    user = User.query.get(session['user_id'])
    order = Order.query.get_or_404(order_id)
    
    if order.shop_id != user.shop.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('seller_orders'))
    
    # Generate QR code for pickup if READY_FOR_PICKUP
    qr_data = None
    if order.status == 'READY_FOR_PICKUP' and order.pickup_token:
        qr_data = generate_qr_code(order.pickup_token)
    
    return render_template('seller_order_detail.html', order=order, qr_data=qr_data)


@app.route('/seller/order/<int:order_id>/mark-ready', methods=['POST'])
@login_required
@role_required('seller')
def mark_order_ready(order_id):
    user = User.query.get(session['user_id'])
    order = Order.query.get_or_404(order_id)
    
    if order.shop_id != user.shop.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('seller_orders'))
    
    if order.status != 'PENDING_PAYMENT':
        flash('Order cannot be marked as ready.', 'warning')
        return redirect(url_for('seller_order_detail', order_id=order_id))
    
    # Generate pickup token for courier
    order.pickup_token = generate_qr_token(order.id, 'pickup')
    order.status = 'READY_FOR_PICKUP'
    db.session.commit()
    
    log_action('ORDER_READY_FOR_PICKUP', 'Order', order.id, f'Order {order.order_number}')
    
    # Notify customer
    send_email(
        order.customer.email,
        'Order Ready for Pickup',
        f'Your order {order.order_number} is ready for pickup!'
    )
    
    flash('Order marked as ready for pickup!', 'success')
    return redirect(url_for('seller_order_detail', order_id=order_id))


# ==================== COURIER ROUTES ====================

@app.route('/courier/dashboard')
@login_required
@role_required('courier')
def courier_dashboard():
    # Show available orders to pickup
    available_orders = Order.query.filter_by(status='READY_FOR_PICKUP', courier_id=None)\
        .order_by(Order.created_at.desc()).all()
    
    # Show assigned orders
    my_orders = Order.query.filter_by(courier_id=session['user_id'])\
        .filter(Order.status.in_(['READY_FOR_PICKUP', 'IN_TRANSIT_TO_RIDER']))\
        .order_by(Order.created_at.desc()).all()
    
    return render_template('courier_dashboard.html', 
        available_orders=available_orders,
        my_orders=my_orders
    )


@app.route('/courier/pickup-manifest')
@login_required
@role_required('courier')
def courier_pickup_manifest():
    # Orders ready for this courier to pickup
    orders = Order.query.filter_by(courier_id=session['user_id'], status='READY_FOR_PICKUP').all()
    return render_template('courier_manifest.html', orders=orders, title='Pickup Manifest')


@app.route('/courier/scan-pickup', methods=['GET', 'POST'])
@login_required
@role_required('courier')
def courier_scan_pickup():
    if request.method == 'POST':
        token = request.form.get('token')
        
        payload = verify_qr_token(token)
        if not payload or payload.get('type') != 'pickup':
            flash('Invalid or expired QR code.', 'danger')
            return redirect(url_for('courier_scan_pickup'))
        
        order = Order.query.get(payload['order_id'])
        if not order or order.status != 'READY_FOR_PICKUP':
            flash('Order not ready for pickup.', 'warning')
            return redirect(url_for('courier_scan_pickup'))
        
        # Assign courier and generate rider token
        order.courier_id = session['user_id']
        order.delivery_token = generate_qr_token(order.id, 'delivery')
        order.status = 'IN_TRANSIT_TO_RIDER'
        db.session.commit()
        
        log_action('ORDER_PICKED_UP', 'Order', order.id, f'Courier picked up {order.order_number}')
        
        # Notify customer
        send_email(
            order.customer.email,
            'Order Picked Up',
            f'Your order {order.order_number} has been picked up and is on the way!'
        )
        
        flash(f'Order {order.order_number} picked up successfully!', 'success')
        return redirect(url_for('courier_dashboard'))
    
    return render_template('courier_scan_pickup.html')


@app.route('/courier/handoff/<int:order_id>')
@login_required
@role_required('courier')
def courier_handoff_qr(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.courier_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('courier_dashboard'))
    
    if order.status != 'IN_TRANSIT_TO_RIDER':
        flash('Order not ready for handoff.', 'warning')
        return redirect(url_for('courier_dashboard'))
    
    # Generate QR for rider to scan
    qr_data = generate_qr_code(order.delivery_token)
    
    return render_template('courier_handoff.html', order=order, qr_data=qr_data)


# ==================== RIDER ROUTES ====================

@app.route('/rider/dashboard')
@login_required
@role_required('rider')
def rider_dashboard():
    # Orders ready for rider pickup from courier
    available_orders = Order.query.filter_by(status='IN_TRANSIT_TO_RIDER', rider_id=None)\
        .order_by(Order.created_at.desc()).all()
    
    # Orders assigned to this rider
    my_orders = Order.query.filter_by(rider_id=session['user_id'])\
        .filter(Order.status.in_(['OUT_FOR_DELIVERY']))\
        .order_by(Order.created_at.desc()).all()
    
    return render_template('rider_dashboard.html',
        available_orders=available_orders,
        my_orders=my_orders
    )


@app.route('/rider/delivery-manifest')
@login_required
@role_required('rider')
def rider_delivery_manifest():
    orders = Order.query.filter_by(rider_id=session['user_id'], status='OUT_FOR_DELIVERY').all()
    return render_template('rider_manifest.html', orders=orders, title='Delivery Manifest')


@app.route('/rider/scan-from-courier', methods=['GET', 'POST'])
@login_required
@role_required('rider')
def rider_scan_from_courier():
    if request.method == 'POST':
        token = request.form.get('token')
        
        payload = verify_qr_token(token)
        if not payload or payload.get('type') != 'delivery':
            flash('Invalid or expired QR code.', 'danger')
            return redirect(url_for('rider_scan_from_courier'))
        
        order = Order.query.get(payload['order_id'])
        if not order or order.status != 'IN_TRANSIT_TO_RIDER':
            flash('Order not available for pickup.', 'warning')
            return redirect(url_for('rider_scan_from_courier'))
        
        # Assign rider
        order.rider_id = session['user_id']
        order.status = 'OUT_FOR_DELIVERY'
        db.session.commit()
        
        log_action('ORDER_OUT_FOR_DELIVERY', 'Order', order.id, f'Rider received {order.order_number}')
        
        # Notify customer
        send_email(
            order.customer.email,
            'Order Out for Delivery',
            f'Your order {order.order_number} is out for delivery!'
        )
        
        flash(f'Order {order.order_number} received for delivery!', 'success')
        return redirect(url_for('rider_dashboard'))
    
    return render_template('rider_scan_courier.html')


@app.route('/rider/confirm-delivery/<int:order_id>', methods=['GET', 'POST'])
@login_required
@role_required('rider')
def rider_confirm_delivery(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.rider_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('rider_dashboard'))
    
    if order.status != 'OUT_FOR_DELIVERY':
        flash('Order not ready for delivery confirmation.', 'warning')
        return redirect(url_for('rider_dashboard'))
    
    if request.method == 'POST':
        # Customer should scan QR to confirm
        token = request.form.get('token')
        
        payload = verify_qr_token(token)
        if not payload or payload.get('type') != 'delivery' or payload['order_id'] != order_id:
            flash('Invalid delivery confirmation.', 'danger')
            return redirect(url_for('rider_confirm_delivery', order_id=order_id))
        
        order.status = 'DELIVERED'
        db.session.commit()
        
        log_action('ORDER_DELIVERED', 'Order', order.id, f'Order {order.order_number} delivered')
        
        # Notify customer and seller
        send_email(
            order.customer.email,
            'Order Delivered',
            f'Your order {order.order_number} has been delivered successfully!'
        )
        
        flash(f'Order {order.order_number} delivered successfully!', 'success')
        return redirect(url_for('rider_dashboard'))
    
    # Show QR for customer to scan
    qr_data = generate_qr_code(order.delivery_token)
    return render_template('rider_delivery_confirm.html', order=order, qr_data=qr_data)


@app.route('/rider/history')
@login_required
@role_required('rider')
def rider_history():
    orders = Order.query.filter_by(rider_id=session['user_id'])\
        .order_by(Order.updated_at.desc()).all()
    return render_template('rider_history.html', orders=orders)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Get filter parameter
    time_filter = request.args.get('filter', 'all')
    
    # Calculate date range based on filter
    now = datetime.utcnow()
    if time_filter == 'day':
        start_date = now - timedelta(days=1)
    elif time_filter == 'week':
        start_date = now - timedelta(weeks=1)
    elif time_filter == 'month':
        start_date = now - timedelta(days=30)
    elif time_filter == 'year':
        start_date = now - timedelta(days=365)
    else:
        start_date = None
    
    # Base query for orders
    order_query = Order.query
    if start_date:
        order_query = order_query.filter(Order.created_at >= start_date)
    
    # Statistics
    total_users = User.query.count()
    total_buyers = User.query.filter_by(role='customer').count()
    total_sellers = User.query.filter_by(role='seller').count()
    total_riders = User.query.filter(User.role.in_(['rider', 'courier'])).count()
    total_orders = Order.query.count()
    total_products = Product.query.count()
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    # Revenue and commission tracking
    total_revenue = db.session.query(func.sum(Order.total_amount))\
        .filter(Order.status == 'DELIVERED')
    if start_date:
        total_revenue = total_revenue.filter(Order.created_at >= start_date)
    total_revenue = total_revenue.scalar() or 0
    
    # Commission received (from delivered orders)
    commission_received = db.session.query(func.sum(Order.commission_amount))\
        .filter(Order.status == 'DELIVERED')
    if start_date:
        commission_received = commission_received.filter(Order.created_at >= start_date)
    commission_received = commission_received.scalar() or 0
    
    # Commission pending (from non-delivered orders)
    commission_pending = db.session.query(func.sum(Order.commission_amount))\
        .filter(Order.status.in_(['PENDING_PAYMENT', 'READY_FOR_PICKUP', 'IN_TRANSIT_TO_RIDER', 'OUT_FOR_DELIVERY']))
    if start_date:
        commission_pending = commission_pending.filter(Order.created_at >= start_date)
    commission_pending = commission_pending.scalar() or 0
    
    # Revenue data for chart (last 7 days/weeks/months depending on filter)
    revenue_chart_data = []
    if time_filter == 'day' or time_filter == 'week':
        # Daily data for last 7 days
        for i in range(6, -1, -1):
            date = now - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            daily_revenue = db.session.query(func.sum(Order.total_amount))\
                .filter(Order.created_at >= day_start, Order.created_at < day_end,
                        Order.status == 'DELIVERED').scalar() or 0
            
            revenue_chart_data.append({
                'label': day_start.strftime('%b %d'),
                'value': float(daily_revenue)
            })
    elif time_filter == 'month':
        # Weekly data for last 4 weeks
        for i in range(3, -1, -1):
            week_start = now - timedelta(weeks=i+1)
            week_end = now - timedelta(weeks=i)
            
            weekly_revenue = db.session.query(func.sum(Order.total_amount))\
                .filter(Order.created_at >= week_start, Order.created_at < week_end,
                        Order.status == 'DELIVERED').scalar() or 0
            
            revenue_chart_data.append({
                'label': f'Week {i+1}',
                'value': float(weekly_revenue)
            })
    else:
        # Monthly data for last 12 months
        for i in range(11, -1, -1):
            month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = now
            else:
                month_end = (now - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_revenue = db.session.query(func.sum(Order.total_amount))\
                .filter(Order.created_at >= month_start, Order.created_at < month_end,
                        Order.status == 'DELIVERED').scalar() or 0
            
            revenue_chart_data.append({
                'label': month_start.strftime('%b %Y'),
                'value': float(monthly_revenue)
            })
    
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html',
        total_users=total_users,
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_riders=total_riders,
        total_orders=total_orders,
        total_products=total_products,
        pending_approvals=pending_approvals,
        total_revenue=total_revenue,
        commission_received=commission_received,
        commission_pending=commission_pending,
        revenue_chart_data=revenue_chart_data,
        time_filter=time_filter,
        recent_logs=recent_logs
    )


@app.route('/admin/approvals')
@login_required
@role_required('admin')
def admin_approvals():
    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template('admin_approvals.html', pending_users=pending_users)


@app.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    log_action('USER_APPROVED', 'User', user.id, f'Approved {user.role}: {user.email}')
    
    # Send approval email
    send_email(
        user.email,
        'Account Approved',
        f'Your {user.role} account has been approved! You can now log in.'
    )
    
    flash(f'{user.role.capitalize()} account approved!', 'success')
    return redirect(url_for('admin_approvals'))


@app.route('/admin/reject/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    
    log_action('USER_REJECTED', 'User', user.id, f'Rejected {user.role}: {user.email}')
    
    send_email(
        user.email,
        'Account Application',
        f'Unfortunately, your {user.role} account application was not approved.'
    )
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User account rejected and removed.', 'info')
    return redirect(url_for('admin_approvals'))


@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    role_filter = request.args.get('role', 'all')
    
    query = User.query
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).all()
    
    # Count by role
    role_counts = {
        'all': User.query.count(),
        'customer': User.query.filter_by(role='customer').count(),
        'seller': User.query.filter_by(role='seller').count(),
        'rider': User.query.filter(User.role.in_(['rider', 'courier'])).count(),
    }
    
    return render_template('admin_users.html', 
        users=users, 
        role_filter=role_filter,
        role_counts=role_counts
    )


@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon')
        
        category = Category(name=name, description=description, icon=icon)
        db.session.add(category)
        db.session.commit()
        
        log_action('CATEGORY_CREATED', 'Category', category.id, f'Created: {name}')
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    categories = Category.query.all()
    return render_template('admin_categories.html', categories=categories)


@app.route('/admin/category/<int:category_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    log_action('CATEGORY_DELETED', 'Category', category.id, f'Deleted: {category.name}')
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_categories'))


@app.route('/admin/orders')
@login_required
@role_required('admin')
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/analytics')
@login_required
@role_required('admin')
def admin_analytics():
    # Sales analytics
    from sqlalchemy import func
    
    total_revenue = db.session.query(func.sum(Order.total_amount))\
        .filter(Order.status == 'DELIVERED').scalar() or 0
        
    total_commission = db.session.query(
        func.sum(Order.commission_amount)
    ).filter(Order.status == 'DELIVERED').scalar() or 0

    seller_earnings = db.session.query(
        func.sum(Order.seller_amount)
    ).filter(Order.status == 'DELIVERED').scalar() or 0
    
    orders_by_status = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()
    
    top_products = db.session.query(
        Product.name, func.sum(OrderItem.quantity).label('total')
    ).join(OrderItem).group_by(Product.id)\
        .order_by(func.sum(OrderItem.quantity).desc()).limit(10).all()
    
    
    return render_template('admin_analytics.html',
        total_revenue=total_revenue,
        total_commission=total_commission,
        seller_earnings=seller_earnings,
        orders_by_status=orders_by_status,
        top_products=top_products
    )


@app.route('/messages')
@login_required
def messages_inbox():
    user = User.query.get(session['user_id'])
    
    # Get all conversations where user is either user1 or user2
    conversations = Conversation.query.filter(
        db.or_(
            Conversation.user1_id == user.id,
            Conversation.user2_id == user.id
        )
    ).order_by(Conversation.last_message_at.desc()).all()
    
    # Count unread messages
    unread_count = 0
    for conv in conversations:
        unread_count += Message.query.filter(
            Message.conversation_id == conv.id,
            Message.sender_id != user.id,
            Message.is_read == False
        ).count()
    
    return render_template('messages_inbox.html', 
        conversations=conversations,
        unread_count=unread_count
    )


@app.route('/messages/conversation/<int:conversation_id>')
@login_required
def view_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    user = User.query.get(session['user_id'])
    
    # Check authorization
    if user.id not in [conversation.user1_id, conversation.user2_id]:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('messages_inbox'))
    
    # Mark messages as read
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user.id,
        Message.is_read == False
    ).update({'is_read': True})
    db.session.commit()
    
    messages = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.created_at.asc()).all()
    
    return render_template('conversation.html',
        conversation=conversation,
        messages=messages
    )


@app.route('/messages/send/<int:conversation_id>', methods=['POST'])
@login_required
def send_message(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    user = User.query.get(session['user_id'])
    
    # Check authorization
    if user.id not in [conversation.user1_id, conversation.user2_id]:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    message_text = request.form.get('message_text', '').strip()
    print("DEBUG received message_text =", message_text)
    if not message_text:
        return jsonify({'success': False, 'message': 'Message cannot be empty'}), 400
    
    message = Message(
        conversation_id=conversation_id,
        sender_id=user.id,
        message_text=message_text
    )
    
    conversation.last_message_at = datetime.utcnow()
    
    db.session.add(message)
    db.session.commit()
    
    log_action('MESSAGE_SENT', 'Message', message.id, f'To conversation {conversation_id}')
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'sender_name': user.full_name,
            'message_text': message.message_text,
            'created_at': message.created_at.strftime('%I:%M %p'),
            'is_own': True
        }
    })


@app.route('/messages/start/<int:shop_id>', methods=['POST'])
@login_required
@role_required('customer')
def start_conversation(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    
    # Check if conversation already exists
    existing = Conversation.query.filter(
        db.or_(
            db.and_(Conversation.user1_id == session['user_id'], Conversation.user2_id == shop.seller_id),
            db.and_(Conversation.user1_id == shop.seller_id, Conversation.user2_id == session['user_id'])
        ),
        Conversation.conversation_type == 'buyer_seller',
        Conversation.shop_id == shop_id
    ).first()
    
    if existing:
        return redirect(url_for('view_conversation', conversation_id=existing.id))
    
    # Create new conversation
    conversation = Conversation(
        user1_id=session['user_id'],
        user2_id=shop.seller_id,
        shop_id=shop_id,
        conversation_type='buyer_seller'
    )
    
    db.session.add(conversation)
    db.session.commit()
    
    log_action('CONVERSATION_STARTED', 'Conversation', conversation.id, f'With shop {shop.name}')
    
    return redirect(url_for('view_conversation', conversation_id=conversation.id))


@app.route('/messages/start-with-rider/<int:order_id>', methods=['POST'])
@login_required
def start_conversation_with_rider(order_id):
    """Start conversation between buyer/seller and rider for an order"""
    order = Order.query.get_or_404(order_id)
    user = User.query.get(session['user_id'])
    
    # Verify user is buyer or seller of this order
    if user.role == 'customer' and order.customer_id != user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    
    if user.role == 'seller' and order.shop.seller_id != user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    
    if not order.rider_id:
        flash('No rider assigned to this order yet.', 'warning')
        return redirect(url_for('customer_order_detail', order_id=order_id) if user.role == 'customer' else url_for('seller_order_detail', order_id=order_id))
    
    # Determine conversation type
    if user.role == 'customer':
        conv_type = 'buyer_rider'
        other_user_id = order.rider_id
    else:  # seller
        conv_type = 'seller_rider'
        other_user_id = order.rider_id
    
    # Check if conversation already exists
    existing = Conversation.query.filter(
        db.or_(
            db.and_(Conversation.user1_id == user.id, Conversation.user2_id == other_user_id),
            db.and_(Conversation.user1_id == other_user_id, Conversation.user2_id == user.id)
        ),
        Conversation.conversation_type == conv_type,
        Conversation.order_id == order_id
    ).first()
    
    if existing:
        return redirect(url_for('view_conversation', conversation_id=existing.id))
    
    # Create new conversation
    conversation = Conversation(
        user1_id=user.id,
        user2_id=other_user_id,
        order_id=order_id,
        conversation_type=conv_type
    )
    
    db.session.add(conversation)
    db.session.commit()
    
    log_action('CONVERSATION_STARTED', 'Conversation', conversation.id, f'With rider for order {order.order_number}')
    
    return redirect(url_for('view_conversation', conversation_id=conversation.id))


@app.route('/messages/check-new/<int:conversation_id>')
@login_required
def check_new_messages(conversation_id):
    """AJAX endpoint to check for new messages"""
    conversation = Conversation.query.get_or_404(conversation_id)
    user = User.query.get(session['user_id'])
    
    if user.id not in [conversation.user1_id, conversation.user2_id]:
        return jsonify({'success': False}), 403
    
    last_message_id = request.args.get('last_id', 0, type=int)
    
    new_messages = Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.id > last_message_id
    ).order_by(Message.created_at.asc()).all()
    
    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'id': msg.id,
            'sender_name': msg.sender.full_name,
            'message_text': msg.message_text,
            'created_at': msg.created_at.strftime('%I:%M %p'),
            'is_own': msg.sender_id == user.id
        })
    
    return jsonify({
        'success': True,
        'messages': messages_data
    })

@app.route('/admin/logs')
@login_required
@role_required('admin')
def admin_logs():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc())\
        .paginate(page=page, per_page=50)
    return render_template('admin_logs.html', logs=logs)

@app.route('/admin/delivery-fees')
@login_required
@role_required('admin')
def admin_delivery_fees():
    from sqlalchemy import func
    delivery_fees = DeliveryFee.query.order_by(DeliveryFee.province, DeliveryFee.city).all()
    
    avg_fee = db.session.query(func.avg(DeliveryFee.fee)).scalar() or 0
    min_fee = db.session.query(func.min(DeliveryFee.fee)).scalar() or 0
    max_fee = db.session.query(func.max(DeliveryFee.fee)).scalar() or 0
    
    return render_template('admin_delivery_fees.html',
        delivery_fees=delivery_fees,
        avg_fee=avg_fee,
        min_fee=min_fee,
        max_fee=max_fee
    )


@app.route('/admin/delivery-fees/add', methods=['POST'])
@login_required
@role_required('admin')
def add_delivery_fee():
    city = request.form.get('city')
    province = request.form.get('province')
    fee = request.form.get('fee')
    
    existing = DeliveryFee.query.filter_by(city=city).first()
    if existing:
        flash('Delivery fee for this city already exists.', 'warning')
        return redirect(url_for('admin_delivery_fees'))
    
    delivery_fee = DeliveryFee(city=city, province=province, fee=fee)
    db.session.add(delivery_fee)
    db.session.commit()
    
    log_action('DELIVERY_FEE_ADDED', 'DeliveryFee', delivery_fee.id, f'{city}: ₱{fee}')
    flash(f'Delivery fee added for {city}.', 'success')
    return redirect(url_for('admin_delivery_fees'))


@app.route('/admin/delivery-fees/<int:fee_id>/update', methods=['POST'])
@login_required
@role_required('admin')
def update_delivery_fee(fee_id):
    delivery_fee = DeliveryFee.query.get_or_404(fee_id)
    new_fee = request.form.get('fee')
    old_fee = delivery_fee.fee
    
    delivery_fee.fee = new_fee
    db.session.commit()
    
    log_action('DELIVERY_FEE_UPDATED', 'DeliveryFee', fee_id, 
               f'{delivery_fee.city}: ₱{old_fee} → ₱{new_fee}')
    flash(f'Delivery fee updated for {delivery_fee.city}.', 'success')
    return redirect(url_for('admin_delivery_fees'))
# ==================== API ROUTES FOR QR SCANNING ====================

@app.route('/api/qr/verify', methods=['POST'])
@login_required
def api_verify_qr():
    """Verify QR token and return order info"""
    token = request.json.get('token')
    
    payload = verify_qr_token(token)
    if not payload:
        return jsonify({'success': False, 'message': 'Invalid or expired token'}), 400
    
    order = Order.query.get(payload['order_id'])
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'order_number': order.order_number,
        'status': order.status,
        'type': payload['type']
    })


# ==================== INITIALIZE DATABASE ====================

@app.before_request
def create_tables():
    """Create tables on first request"""
    if not hasattr(app, 'tables_created'):
        db.create_all()
        
        # Create default admin if not exists
        admin = User.query.filter_by(email='admin@epicuremart.com').first()
        if not admin:
            admin = User(
                email='admin@epicuremart.com',
                role='admin',
                full_name='System Admin',
                is_verified=True,
                is_approved=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create default categories
        if Category.query.count() == 0:
            categories = [
                Category(name='Baking Supplies & Ingredients', icon='🧁'),
                Category(name='Coffee, Tea & Beverages', icon='☕'),
                Category(name='Snacks & Candy', icon='🍬'),
                Category(name='Specialty Foods & International Cuisines', icon='🌍'),
                Category(name='Organic and Health Foods', icon='🥗'),
                Category(name='Meal Kits & Prepped Foods', icon='🍱')
            ]
            db.session.add_all(categories)
        
        db.session.commit()
        app.tables_created = True


@app.route('/api/calabarzon-addresses')
def get_calabarzon_addresses():
    """API endpoint to get CALABARZON address data"""
    import json
    filepath = os.path.join(app.static_folder, 'calabarzon_addresses.json')
    with open(filepath, 'r') as f:
        data = json.load(f)
    return jsonify(data)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)