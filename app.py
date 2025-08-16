"""
Project Title: Employee Leave Management System (ELMS) – Flask Application

Objective: Develop a secure, role-based Flask web application that allows employees to apply for leave 
and enables managers to review, approve, or reject requests.
The system should include real-time status updates, history tracking, and admin-level reporting.
"""

# Author: Nalajala Akhila
# Date: 26-07-2025

# TODO: To restructure the program for efficient template rendering and improved UI aesthetics

# Essential libraries needed for the program implementation
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from enum import Enum

# Initializing the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leave_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Using SQLAlchemy for ORM - chose this over raw SQL for easier model management
# and to prevent SQL injection risks that our security audit flagged last quarter
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User roles for the ELMS
class Role(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'

class LeaveStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

class LeaveType(Enum):
    ANNUAL = 'annual'
    SICK = 'sick'
    MATERNITY = 'maternity'
    PATERNITY = 'paternity'
    EMERGENCY = 'emergency'
    UNPAID = 'unpaid'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.EMPLOYEE)
    department = db.Column(db.String(100))
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships between users
    leave_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.employee_id', backref='employee')
    managed_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.manager_id', backref='manager')
    audit_logs = db.relationship('AuditLog', backref='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'department': self.department,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Leave request model
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    leave_type = db.Column(db.Enum(LeaveType), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.Enum(LeaveStatus), default=LeaveStatus.PENDING)
    manager_comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}",
            'manager_id': self.manager_id,
            'manager_name': f"{self.manager.first_name} {self.manager.last_name}" if self.manager else None,
            'leave_type': self.leave_type.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'days_requested': self.days_requested,
            'reason': self.reason,
            'status': self.status.value,
            'manager_comments': self.manager_comments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }

# Audit log model
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }

# Login manager user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inject current datetime into templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Utility functions
def log_audit(action, resource_type, resource_id=None, details=None):
    """Log user actions for audit trail"""
    if current_user.is_authenticated:
        audit_log = AuditLog(
            user_id=current_user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()

def require_role(required_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in required_roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_working_days(start, end):
    """Counts workdays between dates (excludes weekends). 
    NOTE: We don't handle holidays here - see HR's holiday list API instead.
    """
    days = 0
    day = start
    while day <= end:
        # Skip Sat/Sun
        if day.weekday() not in (5, 6):  
            days += 1
        day += timedelta(days=1)  # increment day
    return days

# HTML Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# login.html file is used here
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            log_audit('LOGIN', 'USER', user.id, 'User logged in successfully')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    log_audit('LOGOUT', 'USER', current_user.id, 'User logged out')
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

# Dashboard.html is used here
# User Roles: Admin, Manager, Employee
@app.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    stats = {}
    
    if current_user.role == Role.ADMIN:
        stats = {
            'total_employees': User.query.filter_by(role=Role.EMPLOYEE, is_active=True).count(),
            'total_managers': User.query.filter_by(role=Role.MANAGER, is_active=True).count(),
            'pending_requests': LeaveRequest.query.filter_by(status=LeaveStatus.PENDING).count(),
            'approved_requests': LeaveRequest.query.filter_by(status=LeaveStatus.APPROVED).count(),
            'rejected_requests': LeaveRequest.query.filter_by(status=LeaveStatus.REJECTED).count(),
        }
    elif current_user.role == Role.MANAGER:
        managed_employees = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in managed_employees]
        
        stats = {
            'team_size': len(managed_employees),
            'pending_requests': LeaveRequest.query.filter(
                LeaveRequest.employee_id.in_(employee_ids),
                LeaveRequest.status == LeaveStatus.PENDING
            ).count(),
            'approved_requests': LeaveRequest.query.filter(
                LeaveRequest.employee_id.in_(employee_ids),
                LeaveRequest.status == LeaveStatus.APPROVED
            ).count(),
        }
    else:
        stats = {
            'pending_requests': LeaveRequest.query.filter_by(
                employee_id=current_user.id, status=LeaveStatus.PENDING
            ).count(),
            'approved_requests': LeaveRequest.query.filter_by(
                employee_id=current_user.id, status=LeaveStatus.APPROVED
            ).count(),
            'rejected_requests': LeaveRequest.query.filter_by(
                employee_id=current_user.id, status=LeaveStatus.REJECTED
            ).count(),
            'total_days_taken': db.session.query(db.func.sum(LeaveRequest.days_requested)).filter(
                LeaveRequest.employee_id == current_user.id,
                LeaveRequest.status == LeaveStatus.APPROVED,
                LeaveRequest.start_date >= datetime.now().replace(month=1, day=1).date()
            ).scalar() or 0
        }
    
    # Get recent leave requests
    if current_user.role == Role.ADMIN:
        recent_requests = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).limit(5).all()
    elif current_user.role == Role.MANAGER:
        managed_employees = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in managed_employees]
        recent_requests = LeaveRequest.query.filter(
            LeaveRequest.employee_id.in_(employee_ids)
        ).order_by(LeaveRequest.created_at.desc()).limit(5).all()
    else:
        recent_requests = LeaveRequest.query.filter_by(
            employee_id=current_user.id
        ).order_by(LeaveRequest.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, recent_requests=recent_requests)

# Employees: Apply for leave, view status, edit or cancel requests
@app.route('/leave-requests')
@login_required
def leave_requests():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    
    query = LeaveRequest.query
    
    # Role-based filtering
    if current_user.role == Role.EMPLOYEE:
        query = query.filter_by(employee_id=current_user.id)
    elif current_user.role == Role.MANAGER:
        managed_employees = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in managed_employees] + [current_user.id]
        query = query.filter(LeaveRequest.employee_id.in_(employee_ids))
    
    # Apply status filter
    if status_filter:
        query = query.filter_by(status=LeaveStatus(status_filter))
    
    requests = query.order_by(LeaveRequest.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('leave_requests.html', requests=requests, status_filter=status_filter)

# Employee creates new leave request
@app.route('/leave-requests/new', methods=['GET', 'POST'])
@login_required
def new_leave_request():
    if request.method == 'POST':
        try:
            leave_type = LeaveType(request.form['leave_type'])
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            reason = request.form['reason']
            
            # Validation
            if start_date > end_date:
                flash('Start date must be before end date', 'error')
                return render_template('new_leave_request.html')
            
            if start_date < datetime.now().date():
                flash('Cannot request leave for past dates', 'error')
                return render_template('new_leave_request.html')
            
            days_requested = get_working_days(start_date, end_date)
            
            # Assign to manager if employee has one
            manager = User.query.get(current_user.manager_id) if current_user.manager_id else None
            
            leave_request = LeaveRequest(
                employee_id=current_user.id,
                manager_id=manager.id if manager else None,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                days_requested=days_requested,
                reason=reason
            )
            
            db.session.add(leave_request)
            db.session.commit()
            
            log_audit('CREATE', 'LEAVE_REQUEST', leave_request.id, 
                     f'Created leave request for {days_requested} days')
            
            flash('Leave request submitted successfully!', 'success')
            return redirect(url_for('leave_requests'))
        
        except Exception as e:
            flash(f'Error creating leave request: {str(e)}', 'error')
    
    return render_template('new_leave_request.html')

# View leave request details
@app.route('/leave-requests/<int:request_id>')
@login_required
def view_leave_request(request_id):
    leave_request = LeaveRequest.query.get_or_404(request_id)
    
    # Check permissions
    if (current_user.role == Role.EMPLOYEE and leave_request.employee_id != current_user.id):
        flash('Access denied', 'error')
        return redirect(url_for('leave_requests'))
    
    if (current_user.role == Role.MANAGER and 
        leave_request.employee_id != current_user.id and 
        leave_request.manager_id != current_user.id):
        flash('Access denied', 'error')
        return redirect(url_for('leave_requests'))
    
    return render_template('view_leave_request.html', leave_request=leave_request)

# Managers: Approve/reject leave, filter by date/employee/status
# Manager can approve or reject the leaves
@app.route('/leave-requests/<int:request_id>/approve', methods=['POST'])
@require_role([Role.MANAGER, Role.ADMIN])
def approve_leave_request(request_id):
    leave_request = LeaveRequest.query.get_or_404(request_id)
    
    # Manager can only approve their team's requests
    if (current_user.role == Role.MANAGER and 
        leave_request.manager_id != current_user.id):
        flash('Access denied', 'error')
        return redirect(url_for('leave_requests'))
    
    if leave_request.status != LeaveStatus.PENDING:
        flash('Request is not pending', 'error')
        return redirect(url_for('view_leave_request', request_id=request_id))
    
    leave_request.status = LeaveStatus.APPROVED
    leave_request.manager_comments = request.form.get('comments', '')
    leave_request.approved_at = datetime.utcnow()
    leave_request.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_audit('APPROVE', 'LEAVE_REQUEST', leave_request.id, 
             f'Approved leave request for {leave_request.employee.username}')
    
    flash('Leave request approved successfully!', 'success')
    return redirect(url_for('view_leave_request', request_id=request_id))

@app.route('/leave-requests/<int:request_id>/reject', methods=['POST'])
@require_role([Role.MANAGER, Role.ADMIN])
def reject_leave_request(request_id):
    leave_request = LeaveRequest.query.get_or_404(request_id)
    
    # Manager can only reject their team's requests
    if (current_user.role == Role.MANAGER and 
        leave_request.manager_id != current_user.id):
        flash('Access denied', 'error')
        return redirect(url_for('leave_requests'))
    
    if leave_request.status != LeaveStatus.PENDING:
        flash('Request is not pending', 'error')
        return redirect(url_for('view_leave_request', request_id=request_id))
    
    comments = request.form.get('comments')
    if not comments:
        flash('Rejection reason is required', 'error')
        return redirect(url_for('view_leave_request', request_id=request_id))
    
    leave_request.status = LeaveStatus.REJECTED
    leave_request.manager_comments = comments
    leave_request.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_audit('REJECT', 'LEAVE_REQUEST', leave_request.id, 
             f'Rejected leave request for {leave_request.employee.username}')
    
    flash('Leave request rejected', 'info')
    return redirect(url_for('view_leave_request', request_id=request_id))

@app.route('/leave-requests/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_leave_request(request_id):
    leave_request = LeaveRequest.query.get_or_404(request_id)
    
    # Only employee can cancel their own requests
    if leave_request.employee_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('leave_requests'))
    
    if leave_request.status in [LeaveStatus.CANCELLED, LeaveStatus.REJECTED]:
        flash('Request already cancelled or rejected', 'error')
        return redirect(url_for('view_leave_request', request_id=request_id))
    
    leave_request.status = LeaveStatus.CANCELLED
    leave_request.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_audit('CANCEL', 'LEAVE_REQUEST', leave_request.id, 'Cancelled leave request')
    
    flash('Leave request cancelled', 'info')
    return redirect(url_for('view_leave_request', request_id=request_id))

# Admin: view full dashboard with metrics and user management
@app.route('/users')
@require_role([Role.ADMIN])
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('users.html', users=users)

# Admin can add new users
@app.route('/users/new', methods=['GET', 'POST'])
@require_role([Role.ADMIN])
def new_user():
    if request.method == 'POST':
        try:
            # Check if user already exists
            if User.query.filter_by(username=request.form['username']).first():
                flash('Username already exists', 'error')
                return render_template('new_user.html')
            
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email already exists', 'error')
                return render_template('new_user.html')
            
            user = User(
                username=request.form['username'],
                email=request.form['email'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                role=Role(request.form['role']),
                department=request.form.get('department'),
                manager_id=request.form.get('manager_id') if request.form.get('manager_id') else None
            )
            user.set_password(request.form['password'])
            
            db.session.add(user)
            db.session.commit()
            
            log_audit('CREATE', 'USER', user.id, f'Created user: {user.username}')
            flash('User created successfully!', 'success')
            return redirect(url_for('users'))
        
        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'error')
    
    managers = User.query.filter_by(role=Role.MANAGER, is_active=True).all()
    return render_template('new_user.html', managers=managers)

# View and edit user profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.email = request.form['email']
        current_user.department = request.form.get('department')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    
    return render_template('profile.html')

# Change password functionality
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        log_audit('PASSWORD_CHANGE', 'USER', current_user.id, 'Password changed successfully')
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html')

# Reports for admin and managers
@app.route('/reports')
@require_role([Role.MANAGER, Role.ADMIN])
def reports():
    return render_template('reports.html')

@app.route('/reports/generate', methods=['GET', 'POST'])
@require_role([Role.MANAGER, Role.ADMIN])
def generate_report():
    """Generate reports in CSV or PDF format based on filters and report type.
    Handles both form submissions (POST) and quick report links (GET).
    """
    # Handle both form submission (POST) and quick reports (GET)
    if request.method == 'POST':
        report_type = request.form['report_type']
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        department = request.form.get('department')
        format_type = request.form.get('format', 'csv')
    else:  # GET request for quick reports
        report_type = request.args.get('report_type', 'leave_summary')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        format_type = request.args.get('format', 'csv')
    
    # Explicit join to avoid ambiguity
    query = db.session.query(LeaveRequest, User).join(
        User, LeaveRequest.employee_id == User.id
    )
    
    # Apply filters based on report type
    if report_type == 'monthly_summary':
        first_day = datetime.now().replace(day=1).date()
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        query = query.filter(LeaveRequest.start_date >= first_day,
                           LeaveRequest.end_date <= last_day)
    elif report_type == 'pending_requests':
        query = query.filter(LeaveRequest.status == LeaveStatus.PENDING)
    elif report_type == 'team_usage' and current_user.role == Role.MANAGER:
        managed_employees = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in managed_employees]
        query = query.filter(LeaveRequest.employee_id.in_(employee_ids))
    elif report_type == 'leave_balance':
        # This would need custom implementation based on your leave balance logic
        pass
    
    # Apply additional filters if provided
    if start_date:
        query = query.filter(LeaveRequest.start_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(LeaveRequest.end_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    if department:
        query = query.filter(User.department == department)
    
    # Role-based filtering
    if current_user.role == Role.MANAGER and report_type != 'team_usage':
        managed_employees = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in managed_employees]
        query = query.filter(LeaveRequest.employee_id.in_(employee_ids))
    
    # Execute query and unpack results
    results = query.all()
    requests = [req for req, user in results]  # Extract just the LeaveRequest objects
    
    if format_type == 'csv':
        return generate_csv_report(requests)
    elif format_type == 'pdf':
        return generate_leave_pdf(requests)

def generate_csv_report(requests):
    """Generate CSV report of leave requests"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header are written
    writer.writerow([
        'Employee Name', 'Department', 'Leave Type', 'Start Date', 'End Date',
        'Days Requested', 'Status', 'Reason', 'Manager Comments', 'Created At'
    ])
    
    #Data is written
    for req in requests:
        writer.writerow([
            f"{req.employee.first_name} {req.employee.last_name}",
            req.employee.department,
            req.leave_type.value,
            req.start_date,
            req.end_date,
            req.days_requested,
            req.status.value,
            req.reason,
            req.manager_comments,
            req.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'leave_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )

def generate_leave_pdf(leave_requests):
    """Generate company-branded PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles for company branding
    company_style = ParagraphStyle(
        name="CompanyStyle",
        fontSize=14,
        textColor=colors.HexColor("#2EA5AB"),  # Company color
        fontName="Helvetica-Bold",
        spaceAfter=20
    )
    
    story = []
    
    # Title with company branding
    title = Paragraph("Employee Leave Management System Report", company_style)
    story.append(title)
    
    # Report metadata
    meta = Paragraph(f"""
    <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
    <b>Total Requests:</b> {len(leave_requests)}<br/>
    <b>Generated By:</b> {current_user.first_name} {current_user.last_name}
    """, styles['Normal'])
    story.append(meta)
    story.append(Spacer(1, 20))
    
    # Summary statistics
    approved_count = len([r for r in leave_requests if r.status == LeaveStatus.APPROVED])
    pending_count = len([r for r in leave_requests if r.status == LeaveStatus.PENDING])
    rejected_count = len([r for r in leave_requests if r.status == LeaveStatus.REJECTED])
    
    summary = Paragraph(f"""
    <b>Summary Statistics:</b><br/>
    Approved Requests: {approved_count}<br/>
    Pending Requests: {pending_count}<br/>
    Rejected Requests: {rejected_count}
    """, styles['Normal'])
    story.append(summary)
    story.append(Spacer(1, 20))
    
    # Table data
    data = [['Employee', 'Department', 'Leave Type', 'Start Date', 'End Date', 'Days', 'Status']]
    
    for req in leave_requests:
        data.append([
            f"{req.employee.first_name} {req.employee.last_name}",
            req.employee.department,
            req.leave_type.value,
            req.start_date.strftime('%Y-%m-%d'),
            req.end_date.strftime('%Y-%m-%d'),
            str(req.days_requested),
            req.status.value
        ])
    
    # Create table with styling
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2EABA7")),  # Company color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    
    story.append(table)
    doc.build(story)
    
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'leave_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

# Error Handlers for 404 & 500
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Initializing the  database
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create admin user if none exists
        if not User.query.filter_by(role=Role.ADMIN).first():
            admin = User(
                username='admin',
                email='admin@gmail.com',
                first_name='Nalajala',
                last_name='Akhila',
                role=Role.ADMIN,
                department='Administration',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created default admin user")

        # Create default manager if none exists
        if not User.query.filter_by(role=Role.MANAGER).first():
            manager = User(
                username='manager',
                email='manager@gmail.com',
                first_name='Bokkisam',
                last_name='Kavya',
                role=Role.MANAGER,
                department='Management',
                is_active=True
            )
            manager.set_password('man123')
            db.session.add(manager)
            print("Created default manager user")

        # Create default employee if none exists
        if not User.query.filter_by(role=Role.EMPLOYEE).first():
            employee = User(
                username='employee',
                email='employee@gmail.com',
                first_name='Abhiram',
                last_name='Nalajala',
                role=Role.EMPLOYEE,
                department='Operations',
                manager_id=User.query.filter_by(username='manager').first().id,  # Assign to manager
                is_active=True
            )
            employee.set_password('emp123')
            db.session.add(employee)
            print("Created default employee user")

        db.session.commit()

# Run the application
if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
