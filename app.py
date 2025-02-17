from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')  # Store in env for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dastaavej.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration (Use env variables for security)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'riyasolanki525@student.sfit.ac.in')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'vfdp cjli cgtq onqc')

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='citizen')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    application_type = db.Column(db.String(20), nullable=False)  # 'passport' or 'pan'
    status = db.Column(db.String(20), default='Pending')
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# Role-based access decorator
def requires_role(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(current_user, *args, **kwargs)
        return wrapped
    return wrapper

# Notification functions
def send_email_notification(email, subject, body):
    try:
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = body
        mail.send(msg)
    except Exception as e:
        print(f"Email notification failed: {str(e)}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    required_fields = ['aadhaar_number', 'password', 'email', 'phone']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(aadhaar_number=data['aadhaar_number']).first():
        return jsonify({'error': 'Aadhaar number already registered'}), 400

    user = User(
        aadhaar_number=data['aadhaar_number'],
        password_hash=generate_password_hash(data['password']),
        email=data['email'],
        phone=data['phone']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(aadhaar_number=data.get('aadhaar_number')).first()

    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'])
    
    return jsonify({'token': token})

@app.route('/api/applications/submit', methods=['POST'])
@token_required
def submit_application(current_user):
    data = request.form.to_dict()
    files = request.files

    application = Application(user_id=current_user.id, application_type=data.get('application_type', ''))
    db.session.add(application)
    db.session.flush()

    for file_key, file in files.items():
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            document = Document(application_id=application.id, document_type=file_key, file_path=filepath)
            db.session.add(document)

    db.session.commit()

    send_email_notification(current_user.email, 'Application Submitted', f'Your application ID is: {application.id}')
    
    return jsonify({'message': 'Application submitted successfully', 'application_id': application.id})

@app.route('/api/applications/<int:application_id>/status', methods=['PUT'])
@token_required
@requires_role('admin')
def update_application_status(current_user, application_id):
    data = request.json
    application = Application.query.get_or_404(application_id)

    application.status = data.get('status', application.status)
    application.rejection_reason = data.get('rejection_reason', application.rejection_reason)

    db.session.commit()

    user = User.query.get(application.user_id)
    send_email_notification(user.email, 'Application Status Updated', f'Your application status is now: {application.status}')
    
    return jsonify({'message': 'Status updated successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
