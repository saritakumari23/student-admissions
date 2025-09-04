import os
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import uuid
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///admissions.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Use temp directory for uploads on Render
if os.environ.get('RENDER'):
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
else:
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)

# Database Models
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    program = db.Column(db.String(100), nullable=False)
    previous_education = db.Column(db.Text, nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    degree_certificate = db.Column(db.String(255), nullable=False)
    id_proof = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.String(100))
    admission_letter_path = db.Column(db.String(255))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Forms
class ApplicationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    date_of_birth = StringField('Date of Birth (YYYY-MM-DD)', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10)])
    program = SelectField('Program', choices=[
        ('computer_science', 'Computer Science'),
        ('engineering', 'Engineering'),
        ('business', 'Business Administration'),
        ('arts', 'Arts and Humanities'),
        ('science', 'Natural Sciences')
    ], validators=[DataRequired()])
    previous_education = TextAreaField('Previous Education', validators=[DataRequired()])
    gpa = StringField('GPA (0.0-4.0)', validators=[DataRequired()])
    degree_certificate = FileField('Degree Certificate', validators=[DataRequired()])
    id_proof = FileField('ID Proof', validators=[DataRequired()])
    submit = SubmitField('Submit Application')

    def validate_gpa(self, field):
        try:
            gpa = float(field.data)
            if not 0.0 <= gpa <= 4.0:
                raise ValueError()
        except ValueError:
            raise ValidationError('GPA must be a number between 0.0 and 4.0')

    def validate_date_of_birth(self, field):
        try:
            datetime.strptime(field.data, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Date must be in YYYY-MM-DD format')

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    form = ApplicationForm()
    if form.validate_on_submit():
        try:
            # Generate unique application ID
            application_id = f"APP{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            
            # Save uploaded files
            degree_cert = form.degree_certificate.data
            id_proof_file = form.id_proof.data
            
            if not degree_cert or not id_proof_file:
                flash('Please upload both required documents.', 'error')
                return render_template('apply.html', form=form)
            
            degree_filename = secure_filename(f"{application_id}_degree_{degree_cert.filename}")
            id_filename = secure_filename(f"{application_id}_id_{id_proof_file.filename}")
            
            # Save files with error handling
            try:
                degree_cert.save(os.path.join(app.config['UPLOAD_FOLDER'], degree_filename))
                id_proof_file.save(os.path.join(app.config['UPLOAD_FOLDER'], id_filename))
            except Exception as e:
                app.logger.error(f"File save error: {str(e)}")
                flash('Error saving uploaded files. Please try again.', 'error')
                return render_template('apply.html', form=form)
            
            # Create application record
            application = Application(
                application_id=application_id,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                date_of_birth=datetime.strptime(form.date_of_birth.data, '%Y-%m-%d').date(),
                address=form.address.data,
                program=form.program.data,
                previous_education=form.previous_education.data,
                gpa=float(form.gpa.data),
                degree_certificate=degree_filename,
                id_proof=id_filename
            )
            
            db.session.add(application)
            db.session.commit()
            
            flash(f'Application submitted successfully! Your application ID is: {application_id}', 'success')
            return redirect(url_for('application_status', application_id=application_id))
            
        except Exception as e:
            app.logger.error(f"Application submission error: {str(e)}")
            app.logger.error(traceback.format_exc())
            db.session.rollback()
            flash('An error occurred while submitting your application. Please try again.', 'error')
            return render_template('apply.html', form=form)
    
    return render_template('apply.html', form=form)

@app.route('/status/<application_id>')
def application_status(application_id):
    application = Application.query.filter_by(application_id=application_id).first()
    if not application:
        flash('Application not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('status.html', application=application)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.password == form.password.data:  # In production, use proper password hashing
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/dashboard')
def admin_dashboard():
    applications = Application.query.order_by(Application.submitted_at.desc()).all()
    return render_template('admin_dashboard.html', applications=applications)

@app.route('/admin/application/<int:app_id>')
def admin_view_application(app_id):
    application = Application.query.get_or_404(app_id)
    return render_template('admin_view_application.html', application=application)

@app.route('/admin/approve/<int:app_id>')
def approve_application(app_id):
    application = Application.query.get_or_404(app_id)
    application.status = 'approved'
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = 'Admin'  # In production, get from session
    
    # Generate admission letter
    admission_letter_path = generate_admission_letter(application)
    application.admission_letter_path = admission_letter_path
    
    db.session.commit()
    flash(f'Application {application.application_id} approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:app_id>')
def reject_application(app_id):
    application = Application.query.get_or_404(app_id)
    application.status = 'rejected'
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = 'Admin'  # In production, get from session
    
    db.session.commit()
    flash(f'Application {application.application_id} rejected!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/download_letter/<int:app_id>')
def download_admission_letter(app_id):
    try:
        application = Application.query.get_or_404(app_id)
        if application.status != 'approved' or not application.admission_letter_path:
            flash('Admission letter not available!', 'error')
            return redirect(url_for('application_status', application_id=application.application_id))
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], application.admission_letter_path)
        
        if not os.path.exists(file_path):
            flash('Admission letter file not found!', 'error')
            return redirect(url_for('application_status', application_id=application.application_id))
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'admission_letter_{application.application_id}.pdf'
        )
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        flash('Error downloading admission letter. Please try again.', 'error')
        return redirect(url_for('application_status', application_id=application.application_id))

def generate_admission_letter(application):
    """Generate PDF admission letter for approved application"""
    filename = f"admission_letter_{application.application_id}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    title = Paragraph("ADMISSION LETTER", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20
    )
    date_text = f"Date: {datetime.now().strftime('%B %d, %Y')}"
    story.append(Paragraph(date_text, date_style))
    story.append(Spacer(1, 20))
    
    # Student Information
    student_info = [
        ['Application ID:', application.application_id],
        ['Student Name:', f"{application.first_name} {application.last_name}"],
        ['Email:', application.email],
        ['Phone:', application.phone],
        ['Program:', application.program.replace('_', ' ').title()],
        ['GPA:', str(application.gpa)]
    ]
    
    table = Table(student_info, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Admission Letter Content
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=0  # Left alignment
    )
    
    content = f"""
    Dear {application.first_name} {application.last_name},
    
    We are pleased to inform you that your application for admission to our {application.program.replace('_', ' ').title()} program has been approved. 
    Your application ID is {application.application_id}.
    
    Based on your academic background and qualifications, we are confident that you will be a valuable addition to our institution.
    
    Please note the following important information:
    • Your application has been reviewed and approved by our admissions committee
    • You will receive further instructions regarding enrollment procedures
    • Please keep this admission letter for your records
    
    We look forward to welcoming you to our institution and wish you success in your academic journey.
    
    Best regards,
    Admissions Committee
    """
    
    story.append(Paragraph(content, content_style))
    
    doc.build(story)
    return filepath

# Global error handler
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {error}")
    app.logger.error(traceback.format_exc())
    flash('An internal server error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    flash('Page not found.', 'error')
    return redirect(url_for('index'))

# Health check endpoint for Render
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# API Routes for testing
@app.route('/api/applications', methods=['GET'])
def api_get_applications():
    applications = Application.query.all()
    return jsonify([{
        'id': app.id,
        'application_id': app.application_id,
        'first_name': app.first_name,
        'last_name': app.last_name,
        'email': app.email,
        'status': app.status,
        'submitted_at': app.submitted_at.isoformat() if app.submitted_at else None
    } for app in applications])

@app.route('/api/applications/<int:app_id>', methods=['GET'])
def api_get_application(app_id):
    application = Application.query.get_or_404(app_id)
    return jsonify({
        'id': application.id,
        'application_id': application.application_id,
        'first_name': application.first_name,
        'last_name': application.last_name,
        'email': application.email,
        'phone': application.phone,
        'date_of_birth': application.date_of_birth.isoformat(),
        'address': application.address,
        'program': application.program,
        'previous_education': application.previous_education,
        'gpa': application.gpa,
        'status': application.status,
        'submitted_at': application.submitted_at.isoformat() if application.submitted_at else None
    })

if __name__ == '__main__':
    with app.app_context():
        # Handle database URL for Render
        if os.environ.get('DATABASE_URL'):
            # Render provides DATABASE_URL, but SQLAlchemy expects it to start with postgresql://
            # Convert postgres:// to postgresql://
            database_url = os.environ.get('DATABASE_URL')
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
        db.create_all()
        # Create default admin user if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin', password='admin123')
            db.session.add(admin)
            db.session.commit()
    
    # For production deployment on Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
