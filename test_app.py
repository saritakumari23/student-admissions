import pytest
import tempfile
import os
from io import BytesIO
from app import app, db, Application, Admin
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test admin user
            admin = Admin(username='testadmin', password='testpass')
            db.session.add(admin)
            db.session.commit()
            yield client
        db.drop_all()

@pytest.fixture
def sample_application_data():
    return {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '1234567890',
        'date_of_birth': '1995-01-15',
        'address': '123 Main St, City, State 12345',
        'program': 'computer_science',
        'previous_education': 'Bachelor of Science in Computer Science',
        'gpa': '3.8'
    }

class TestApplicationSubmission:
    """Test application submission functionality"""
    
    def test_home_page(self, client):
        """Test that home page loads correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Student Admission System' in response.data
    
    def test_apply_page_loads(self, client):
        """Test that apply page loads correctly"""
        response = client.get('/apply')
        assert response.status_code == 200
        assert b'Student Application Form' in response.data
    
    def test_application_submission_success(self, client, sample_application_data):
        """Test successful application submission"""
        # Create test files
        degree_file = (BytesIO(b'fake degree certificate'), 'degree.pdf')
        id_file = (BytesIO(b'fake id proof'), 'id.pdf')
        
        data = sample_application_data.copy()
        data['degree_certificate'] = degree_file
        data['id_proof'] = id_file
        
        response = client.post('/apply', data=data, content_type='multipart/form-data')
        
        # Should redirect to status page
        assert response.status_code == 302
        
        # Check if application was created in database
        with app.app_context():
            application = Application.query.first()
            assert application is not None
            assert application.first_name == 'John'
            assert application.last_name == 'Doe'
            assert application.email == 'john.doe@example.com'
            assert application.status == 'pending'
    
    def test_application_validation_errors(self, client):
        """Test form validation errors"""
        # Submit form without required fields
        response = client.post('/apply', data={})
        assert response.status_code == 200
        assert b'This field is required' in response.data
    
    def test_invalid_email_format(self, client, sample_application_data):
        """Test email validation"""
        data = sample_application_data.copy()
        data['email'] = 'invalid-email'
        
        response = client.post('/apply', data=data)
        assert response.status_code == 200
        assert b'Invalid email address' in response.data
    
    def test_invalid_gpa_range(self, client, sample_application_data):
        """Test GPA validation"""
        data = sample_application_data.copy()
        data['gpa'] = '5.0'  # Invalid GPA
        
        response = client.post('/apply', data=data)
        assert response.status_code == 200
        assert b'GPA must be a number between 0.0 and 4.0' in response.data

class TestAdminFunctionality:
    """Test admin functionality"""
    
    def test_admin_login_page(self, client):
        """Test admin login page loads"""
        response = client.get('/admin/login')
        assert response.status_code == 200
        assert b'Admin Login' in response.data
    
    def test_admin_login_success(self, client):
        """Test successful admin login"""
        response = client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'testpass'
        })
        assert response.status_code == 302  # Should redirect
    
    def test_admin_login_failure(self, client):
        """Test failed admin login"""
        response = client.post('/admin/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_admin_dashboard_access(self, client):
        """Test admin dashboard access"""
        # First login
        client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'testpass'
        })
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data

class TestApplicationManagement:
    """Test application management by admin"""
    
    def test_approve_application(self, client, sample_application_data):
        """Test approving an application"""
        # Create a test application
        with app.app_context():
            application = Application(
                application_id='TEST123',
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                phone='1234567890',
                date_of_birth=datetime.now().date(),
                address='Test Address',
                program='computer_science',
                previous_education='Test Education',
                gpa=3.5,
                degree_certificate='test_degree.pdf',
                id_proof='test_id.pdf'
            )
            db.session.add(application)
            db.session.commit()
            app_id = application.id
        
        # Approve the application
        response = client.get(f'/admin/approve/{app_id}')
        assert response.status_code == 302  # Should redirect
        
        # Check if application was approved
        with app.app_context():
            application = Application.query.get(app_id)
            assert application.status == 'approved'
            assert application.admission_letter_path is not None
    
    def test_reject_application(self, client, sample_application_data):
        """Test rejecting an application"""
        # Create a test application
        with app.app_context():
            application = Application(
                application_id='TEST456',
                first_name='Jane',
                last_name='Smith',
                email='jane@example.com',
                phone='0987654321',
                date_of_birth=datetime.now().date(),
                address='Test Address',
                program='engineering',
                previous_education='Test Education',
                gpa=3.2,
                degree_certificate='test_degree.pdf',
                id_proof='test_id.pdf'
            )
            db.session.add(application)
            db.session.commit()
            app_id = application.id
        
        # Reject the application
        response = client.get(f'/admin/reject/{app_id}')
        assert response.status_code == 302  # Should redirect
        
        # Check if application was rejected
        with app.app_context():
            application = Application.query.get(app_id)
            assert application.status == 'rejected'

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_get_applications_api(self, client, sample_application_data):
        """Test getting applications via API"""
        # Create a test application
        with app.app_context():
            application = Application(
                application_id='API123',
                first_name='API',
                last_name='Test',
                email='api@test.com',
                phone='1234567890',
                date_of_birth=datetime.now().date(),
                address='API Test Address',
                program='business',
                previous_education='API Test Education',
                gpa=3.7,
                degree_certificate='api_test.pdf',
                id_proof='api_id.pdf'
            )
            db.session.add(application)
            db.session.commit()
        
        response = client.get('/api/applications')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        assert data[0]['application_id'] == 'API123'
    
    def test_get_single_application_api(self, client, sample_application_data):
        """Test getting single application via API"""
        # Create a test application
        with app.app_context():
            application = Application(
                application_id='SINGLE123',
                first_name='Single',
                last_name='Test',
                email='single@test.com',
                phone='1234567890',
                date_of_birth=datetime.now().date(),
                address='Single Test Address',
                program='arts',
                previous_education='Single Test Education',
                gpa=3.9,
                degree_certificate='single_test.pdf',
                id_proof='single_id.pdf'
            )
            db.session.add(application)
            db.session.commit()
            app_id = application.id
        
        response = client.get(f'/api/applications/{app_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['application_id'] == 'SINGLE123'
        assert data['first_name'] == 'Single'

class TestApplicationStatus:
    """Test application status checking"""
    
    def test_application_status_page(self, client, sample_application_data):
        """Test application status page"""
        # Create a test application
        with app.app_context():
            application = Application(
                application_id='STATUS123',
                first_name='Status',
                last_name='Test',
                email='status@test.com',
                phone='1234567890',
                date_of_birth=datetime.now().date(),
                address='Status Test Address',
                program='science',
                previous_education='Status Test Education',
                gpa=3.6,
                degree_certificate='status_test.pdf',
                id_proof='status_id.pdf'
            )
            db.session.add(application)
            db.session.commit()
        
        response = client.get(f'/status/STATUS123')
        assert response.status_code == 200
        assert b'Application Status' in response.data
        assert b'STATUS123' in response.data
    
    def test_invalid_application_id(self, client):
        """Test status check with invalid application ID"""
        response = client.get('/status/INVALID123')
        assert response.status_code == 302  # Should redirect to home

if __name__ == '__main__':
    pytest.main([__file__])
