# app.py - Main Flask Application
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, IntegerField, DecimalField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import datetime, date
import os
import pymysql
import urllib.parse
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed
from functools import wraps

# Configure PyMySQL to be used with SQLAlchemy
pymysql.install_as_MySQLdb()

# Escape the password
password = urllib.parse.quote_plus("Varunloni@12")

app = Flask(__name__)
app.config['SITE_NAME'] = 'Premier Dental Lab'
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@127.0.0.1/dental_lab_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

# Initialize Flask extensions
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# Custom Jinja2 filter for parsing JSON strings
@app.template_filter('fromjson')
def fromjson(value):
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

db = SQLAlchemy(app)

# Database Models
class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class Material(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='material', lazy=True)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='processing')
    payment_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_address = db.Column(db.Text)

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(10))
    features = db.Column(db.Text)  # JSON string of features
    price_range = db.Column(db.String(50))

# User model for authentication
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

# Forms
class AppointmentForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    service = SelectField('Service', validators=[DataRequired()], coerce=str)
    date = DateField('Preferred Date', validators=[DataRequired()])
    time = TimeField('Preferred Time', validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')

class OrderForm(FlaskForm):
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    customer_email = StringField('Email', validators=[DataRequired(), Email()])
    customer_phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    material_id = SelectField('Material', validators=[DataRequired()], coerce=int)
    quantity = IntegerField('Quantity', validators=[DataRequired()], default=1)
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired()])

# Authentication Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

# Additional Forms
class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[Length(min=6, message="Password must be at least 6 characters")])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password', message="Passwords must match")])

    def validate_email(self, email):
        user = User.query.filter(User.email == email.data, User.id != session['user_id']).first()
        if user:
            raise ValidationError('Email is already in use by another account')

class MaterialForm(FlaskForm):
    material_id = HiddenField()
    name = StringField('Material Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    price = DecimalField('Price ($)', validators=[DataRequired()], places=2)
    stock = IntegerField('Stock', validators=[DataRequired()], default=0)
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('Ceramics', 'Ceramics'),
        ('Impressions', 'Impressions'),
        ('Metals', 'Metals'),
        ('Composites', 'Composites')
    ])
    image = FileField('Material Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

class StockAdjustmentForm(FlaskForm):
    material_id = HiddenField(validators=[DataRequired()])
    adjustment = IntegerField('Adjustment', validators=[DataRequired()])
    reason = SelectField('Reason', choices=[
        ('restocking', 'Restocking'),
        ('correction', 'Inventory Correction'),
        ('damaged', 'Damaged/Expired'),
        ('other', 'Other')
    ])
    other_reason = StringField('Other Reason')

# Define upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit for uploads

# Helper function to create upload directory
def ensure_upload_directory():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to create a placeholder image directory
def ensure_image_directory():
    image_dir = os.path.join(app.static_folder, 'images')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        
        # Create a placeholder image file if it doesn't exist
        placeholder_path = os.path.join(image_dir, 'placeholder.jpg')
        if not os.path.exists(placeholder_path):
            # You could add code here to create a simple placeholder image
            # or just leave a note to manually add one
            print("Please add a placeholder.jpg image to the static/images directory")

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Replace deprecated before_first_request with proper initialization
def setup_app():
    # Create tables (though we're using SQL scripts instead)
    # db.create_all()
    
    # Ensure image directory exists
    ensure_image_directory()
    
    # Ensure upload directory exists
    ensure_upload_directory()

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your username and password', 'danger')
    
    return render_template('login.html', form=form, hero_exists=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == form.username.data) | 
                                          (User.email == form.email.data)).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
            return render_template('register.html', form=form, hero_exists=False)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        # Make the first user an admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form, hero_exists=False)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # Get user's appointments and orders
    appointments = Appointment.query.filter_by(email=user.email).all()
    orders = Order.query.filter_by(customer_email=user.email).all()
    
    return render_template('dashboard.html', user=user, appointments=appointments, orders=orders, hero_exists=False)

# Regular Routes
@app.route('/')
def index():
    services = Service.query.all()
    materials = Material.query.limit(4).all()
    return render_template('index.html', services=services, materials=materials, hero_exists=True)

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services, hero_exists=False)

@app.route('/products')
def products():
    materials = Material.query.all()
    return render_template('products.html', materials=materials, hero_exists=False)

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    form = AppointmentForm()
    
    # Populate service choices
    services = Service.query.all()
    form.service.choices = [(service.title, service.title) for service in services]
    
    if form.validate_on_submit():
        appointment = Appointment(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            service=form.service.data,
            date=form.date.data,
            time=form.time.data,
            notes=form.notes.data
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment booked successfully! We will contact you soon.', 'success')
        return redirect(url_for('appointments'))
    
    return render_template('appointments.html', form=form, hero_exists=False)

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    form = OrderForm()
    
    # Populate material choices
    materials = Material.query.all()
    form.material_id.choices = [(material.id, f"{material.name} - ${material.price}") for material in materials]
    
    if form.validate_on_submit():
        material = Material.query.get(form.material_id.data)
        total_price = material.price * form.quantity.data
        
        order = Order(
            customer_name=form.customer_name.data,
            customer_email=form.customer_email.data,
            customer_phone=form.customer_phone.data,
            material_id=form.material_id.data,
            quantity=form.quantity.data,
            total_price=total_price,
            delivery_address=form.delivery_address.data
        )
        
        # Update stock
        material.stock -= form.quantity.data
        
        db.session.add(order)
        db.session.commit()
        
        flash(f'Order placed successfully! Total: ${total_price}', 'success')
        return redirect(url_for('orders'))
    
    # Get recent orders for display
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('orders.html', form=form, recent_orders=recent_orders, hero_exists=False)

@app.route('/about')
def about():
    return render_template('about.html', hero_exists=False)

# API Routes for AJAX requests
@app.route('/api/materials')
def api_materials():
    materials = Material.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'price': float(m.price),
        'stock': m.stock,
        'description': m.description
    } for m in materials])

@app.route('/api/order', methods=['POST'])
def api_order():
    data = request.json
    
    material = Material.query.get(data['material_id'])
    if not material or material.stock < data['quantity']:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    total_price = material.price * data['quantity']
    
    order = Order(
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
        customer_phone=data.get('customer_phone', ''),
        material_id=data['material_id'],
        quantity=data['quantity'],
        total_price=total_price,
        delivery_address=data.get('delivery_address', '')
    )
    
    material.stock -= data['quantity']
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'total_price': float(total_price)
    })

@app.route('/api/appointments', methods=['POST'])
def api_appointment():
    data = request.json
    
    appointment = Appointment(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        service=data['service'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        time=datetime.strptime(data['time'], '%H:%M').time(),
        notes=data.get('notes', '')
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'appointment_id': appointment.id
    })

# Admin routes (basic)
@app.route('/admin')
@admin_required
def admin_dashboard():
    appointments_count = Appointment.query.count()
    orders_count = Order.query.count()
    materials_count = Material.query.count()
    users_count = User.query.count()
    
    # Recent activities
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           appointments_count=appointments_count,
                           orders_count=orders_count,
                           materials_count=materials_count,
                           users_count=users_count,
                           recent_appointments=recent_appointments,
                           recent_orders=recent_orders,
                           hero_exists=False)

@app.route('/admin/appointments')
@admin_required
def admin_appointments():
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    form = FlaskForm()  # Create a basic form just for CSRF token
    return render_template('admin/appointments.html', appointments=appointments, form=form, hero_exists=False)

@app.route('/admin/appointments/update-status/<int:appointment_id>', methods=['POST'])
@admin_required
def update_appointment_status(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    status = request.form.get('status')
    
    if status in ['pending', 'confirmed', 'completed', 'cancelled']:
        appointment.status = status
        db.session.commit()
        flash(f'Appointment status updated to {status}', 'success')
    else:
        flash('Invalid status', 'danger')
        
    return redirect(url_for('admin_appointments'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    form = FlaskForm()  # Create a basic form just for CSRF token
    return render_template('admin/orders.html', orders=orders, form=form, hero_exists=False)

@app.route('/admin/orders/update-status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    
    if status in ['processing', 'completed', 'cancelled']:
        order.status = status
        db.session.commit()
        flash(f'Order status updated to {status}', 'success')
    else:
        flash('Invalid status', 'danger')
        
    return redirect(url_for('admin_orders'))

@app.route('/admin/orders/update-payment/<int:order_id>', methods=['POST'])
@admin_required
def update_payment_status(order_id):
    order = Order.query.get_or_404(order_id)
    payment_status = request.form.get('payment_status')
    
    if payment_status in ['pending', 'paid']:
        order.payment_status = payment_status
        db.session.commit()
        flash(f'Payment status updated to {payment_status}', 'success')
    else:
        flash('Invalid payment status', 'danger')
        
    return redirect(url_for('admin_orders'))

@app.route('/admin/materials')
@admin_required
def admin_materials():
    materials = Material.query.all()
    form = MaterialForm()  # Create form instance for CSRF token
    return render_template('admin/materials.html', materials=materials, form=form, hero_exists=False)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users, hero_exists=False)

@app.route('/test_db')
def test_db():
    try:
        # Import our direct database utilities
        from db_utils import get_all_materials, get_all_services, get_all_appointments, get_all_orders
        
        # Test getting data from tables
        materials = get_all_materials()
        services = get_all_services()
        appointments = get_all_appointments() or []
        orders = get_all_orders() or []
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'data': {
                'materials_count': len(materials) if materials else 0,
                'services_count': len(services) if services else 0,
                'appointment_count': len(appointments),
                'order_count': len(orders)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database connection error: {str(e)}'
        }), 500

# Profile routes
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    form = ProfileForm(obj=user)
    
    if form.validate_on_submit():
        # Verify current password
        if not user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return render_template('profile.html', form=form, hero_exists=False)
        
        # Update email
        user.email = form.email.data
        
        # Update password if provided
        if form.new_password.data:
            user.set_password(form.new_password.data)
            
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('profile.html', form=form, hero_exists=False)

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    # Create a form instance just for CSRF validation
    form = FlaskForm()
    
    user = User.query.get(session['user_id'])
    
    # Verify password
    if not user.check_password(request.form.get('password')):
        flash('Password is incorrect. Account not deleted.', 'danger')
        return redirect(url_for('profile'))
    
    # Delete user's data
    Appointment.query.filter_by(email=user.email).delete()
    Order.query.filter_by(customer_email=user.email).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    # Clear session
    session.clear()
    flash('Your account has been deleted successfully', 'info')
    return redirect(url_for('index'))

# Admin Material Management routes
@app.route('/admin/materials/edit', methods=['POST'])
@admin_required
def admin_materials_edit():
    form = MaterialForm()
    
    if form.validate_on_submit():
        if form.material_id.data:
            # Update existing material
            material = Material.query.get_or_404(form.material_id.data)
            material.name = form.name.data
            material.description = form.description.data
            material.price = form.price.data
            material.stock = form.stock.data
            material.category = form.category.data
            
            # Handle image upload
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                # Add timestamp to filename to prevent caching issues
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.image.data.save(filepath)
                material.image_url = f'/static/uploads/{filename}'
            
            flash('Material updated successfully', 'success')
        else:
            # Create new material
            material = Material(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data,
                category=form.category.data
            )
            
            # Handle image upload
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                # Add timestamp to filename to prevent caching issues
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.image.data.save(filepath)
                material.image_url = f'/static/uploads/{filename}'
            else:
                material.image_url = '/static/images/placeholder.jpg'
                
            db.session.add(material)
            flash('Material added successfully', 'success')
            
        db.session.commit()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")
                
    return redirect(url_for('admin_materials'))

@app.route('/admin/materials/adjust-stock', methods=['POST'])
@admin_required
def admin_adjust_stock():
    form = StockAdjustmentForm()
    
    if form.validate_on_submit():
        material = Material.query.get_or_404(form.material_id.data)
        
        # Adjust stock
        adjustment = form.adjustment.data
        new_stock = material.stock + adjustment
        
        if new_stock < 0:
            flash('Cannot reduce stock below zero', 'danger')
            return redirect(url_for('admin_materials'))
            
        material.stock = new_stock
        
        # Record reason
        reason = form.reason.data
        if reason == 'other' and form.other_reason.data:
            reason = form.other_reason.data
            
        # Here you could also log the adjustment in a separate table if needed
        
        db.session.commit()
        flash(f'Stock adjusted successfully. New stock: {new_stock}', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")
                
    return redirect(url_for('admin_materials'))

@app.route('/admin/materials/delete', methods=['POST'])
@admin_required
def admin_delete_material():
    material_id = request.form.get('material_id')
    material = Material.query.get_or_404(material_id)
    
    # Check if material is used in any orders
    order_count = Order.query.filter_by(material_id=material_id).count()
    if order_count > 0:
        flash(f'Cannot delete material: Used in {order_count} orders', 'danger')
        return redirect(url_for('admin_materials'))
    
    # Delete material
    db.session.delete(material)
    db.session.commit()
    
    flash('Material deleted successfully', 'success')
    return redirect(url_for('admin_materials'))

# API Routes for Material management
@app.route('/api/materials/<int:material_id>')
@login_required
def api_material_detail(material_id):
    material = Material.query.get_or_404(material_id)
    return jsonify({
        'id': material.id,
        'name': material.name,
        'description': material.description,
        'price': float(material.price),
        'stock': material.stock,
        'category': material.category,
        'image_url': material.image_url
    })

if __name__ == '__main__':
    # Call setup function before running the app
    setup_app()
    app.run(debug=True)
