# Student Admission System

A comprehensive web-based application for managing student admissions, built with Python Flask framework. This system provides a complete solution for educational institutions to handle student applications, admin review processes, and automated admission letter generation.

## live :  https://student-admissions.onrender.com

## 🎯 Project Overview

The Student Admission System is designed to streamline the entire admission process from application submission to final decision. It features:

- **Student Portal**: Easy-to-use application form with document upload
- **Admin Dashboard**: Comprehensive interface for reviewing and managing applications
- **Automated PDF Generation**: Automatic admission letter creation for approved applications
- **Real-time Status Tracking**: Students can track their application status
- **Secure Document Management**: Safe file upload and storage system

## 🚀 Features

### For Students
- 📝 **Easy Application Submission**: User-friendly form with validation
- 📁 **Document Upload**: Secure upload of degree certificates and ID proofs
- 🔍 **Status Tracking**: Real-time application status monitoring
- 📄 **Admission Letter Download**: Automatic PDF generation for approved applications

### For Administrators
- 📊 **Dashboard Analytics**: Overview of all applications with statistics
- 👀 **Application Review**: Detailed view of each application
- ✅ **Approve/Reject Actions**: One-click approval or rejection
- 📋 **Comprehensive Management**: Sort, filter, and search applications

## 🛠 Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (development), MySQL/PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **PDF Generation**: ReportLab
- **Testing**: pytest
- **Form Handling**: Flask-WTF, WTForms
- **File Upload**: Werkzeug

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## 🔧 Installation Instructions

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd student-admission-system
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📖 Usage Instructions

### For Students

1. **Submit Application**
   - Visit the home page and click "Apply Now"
   - Fill out the application form with your details
   - Upload required documents (degree certificate and ID proof)
   - Submit the application
   - Note your unique application ID

2. **Track Status**
   - Use your application ID to check status
   - Visit `/status/<application_id>` to view details
   - Monitor progress through the review process

3. **Download Admission Letter**
   - Once approved, download your admission letter
   - Letter will be available as a PDF file

### For Administrators

1. **Login**
   - Navigate to Admin Login page
   - Use default credentials: `admin` / `admin123`
   - Access the admin dashboard

2. **Review Applications**
   - View all applications in the dashboard
   - Click "View" to see detailed information
   - Review uploaded documents and student details

3. **Make Decisions**
   - Click "Approve" or "Reject" buttons
   - System automatically generates admission letters for approved applications
   - Students are notified of status changes

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest test_app.py

# Run with verbose output
pytest -v
```

### Test Coverage
The application includes comprehensive tests covering:
- Application submission and validation
- Admin functionality and authentication
- API endpoints
- File upload handling
- PDF generation
- Error scenarios

## 📁 Project Structure

```
student-admission-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── test_app.py           # Test suite
├── FRD.md                # Functional Requirements Document
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── apply.html
│   ├── status.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── admin_view_application.html
├── uploads/              # File upload directory (created automatically)
└── admissions.db        # SQLite database (created automatically)
```

## 🔐 Security Features

- **Input Validation**: All form inputs are validated and sanitized
- **File Upload Security**: Secure file handling with size limits and type validation
- **SQL Injection Prevention**: Parameterized queries using SQLAlchemy
- **XSS Protection**: Template escaping and input sanitization
- **Secure File Storage**: Files are stored with unique names to prevent conflicts

## 🚀 Deployment

### Render Deployment (Recommended)
The easiest way to deploy this application is using Render:

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Connect to Render**: Follow the [Deployment Guide](DEPLOYMENT_GUIDE.md)
3. **Automatic Deployment**: Render will automatically deploy your app
4. **Access Your App**: Get a URL like `https://your-app-name.onrender.com`

**Quick Deploy Steps:**
- Sign up at [render.com](https://render.com)
- Create new Web Service
- Connect your GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn app:app`
- Deploy!

### Development Environment
The application is configured for development with SQLite database. For production:

1. **Database Setup**
   ```bash
   # Update app.py to use MySQL/PostgreSQL
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:pass@localhost/dbname'
   ```

2. **Environment Variables**
   ```bash
   # Set production secret key
   export FLASK_SECRET_KEY='your-production-secret-key'
   ```

3. **Web Server**
   - Use Gunicorn or uWSGI for production
   - Configure reverse proxy (Nginx/Apache)
   - Set up SSL certificates

## 🔧 Configuration

### Environment Variables
- `FLASK_SECRET_KEY`: Secret key for session management
- `DATABASE_URL`: Database connection string
- `UPLOAD_FOLDER`: File upload directory path
- `MAX_CONTENT_LENGTH`: Maximum file upload size

### Database Configuration
The application uses SQLite by default. For production:
- MySQL: `mysql://user:password@localhost/dbname`
- PostgreSQL: `postgresql://user:password@localhost/dbname`

## 📝 API Documentation

### Endpoints

#### GET /api/applications
Returns list of all applications
```json
[
  {
    "id": 1,
    "application_id": "APP2025010112345678",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "status": "pending",
    "submitted_at": "2025-01-01T12:00:00"
  }
]
```

#### GET /api/applications/{id}
Returns specific application details
```json
{
  "id": 1,
  "application_id": "APP2025010112345678",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "program": "computer_science",
  "gpa": 3.8,
  "status": "approved"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in FRD.md

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - Student application submission
  - Admin dashboard and review system
  - PDF admission letter generation
  - Comprehensive testing suite

## 📋 Assumptions and Design Decisions

### Assumptions
1. **File Storage**: Local file storage is used for simplicity. Production should use cloud storage (AWS S3, Google Cloud Storage)
2. **Authentication**: Basic username/password authentication. Production should implement proper session management and password hashing
3. **Database**: SQLite for development, MySQL/PostgreSQL for production
4. **Email Notifications**: Not implemented in this version. Future versions should include email notifications for status changes

### Design Decisions
1. **Flask Framework**: Chosen for its simplicity and flexibility
2. **SQLAlchemy ORM**: Provides database abstraction and security
3. **Bootstrap UI**: Ensures responsive design and modern appearance
4. **ReportLab**: Industry-standard PDF generation library
5. **Test-Driven Development**: Comprehensive test suite for reliability
6. **Modular Structure**: Separated concerns for maintainability

### Future Enhancements
- Email notification system
- Advanced search and filtering
- Bulk operations for admins
- Mobile application
- Integration with student information systems
- Advanced analytics and reporting
- Multi-language support
- Role-based access control
