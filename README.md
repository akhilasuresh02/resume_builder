# Resume Builder

A modern, user-friendly web application for creating and managing professional resumes. Build your perfect resume in minutes with our intuitive step-by-step interface.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Usage Guide](#usage-guide)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Automation Testing](#automation-testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

Resume Builder is a full-stack web application designed to simplify the resume creation process. Users can register an account, log in, and create multiple professional resumes by filling in their personal information, work experience, education, skills, languages, and achievements. The application generates a formatted resume that can be viewed and exported.

## Features

- **User Authentication**
  - Secure user registration with email validation
  - Login functionality with password hashing using bcrypt
  - User session management

- **Resume Management**
  - Create and manage multiple resumes
  - Step-by-step resume builder interface
  - Add personal information (name, email, phone, summary)
  - Track work experience
  - Add skills and proficiencies
  - Include education history
  - List languages
  - Highlight achievements

- **Resume Generation**
  - Professional resume preview
  - Formatted resume layout
  - Clean and printable design

- **Responsive Design**
  - Mobile-friendly interface
  - Cross-browser compatibility
  - Intuitive user dashboard

## Screenshots

### Landing Page
The welcoming landing page showcases the application's key features and includes a clear call-to-action button.

<img width="1918" height="958" alt="landing page" src="https://github.com/user-attachments/assets/a08b37a4-da91-43ec-bb24-673368136324" />


**Features highlighted:**
- Easy to Use: Simple and intuitive interface
- Standard ATS Template: ATS-friendly resume format
- Export Ready: Download resumes in PDF format

### Login Page
Clean and professional login interface with seamless user authentication.

<img width="1897" height="970" alt="login" src="https://github.com/user-attachments/assets/6187bc47-44b2-47cc-9b6f-03d4622a3ae3" />


## Tech Stack

- **Backend**: Flask 2.3.2
- **Database**: 
  - SQLite (development)
  - PostgreSQL 13 (production)
- **Authentication**: Flask-Bcrypt 1.0.1
- **ORM/Database**: Flask-SQLAlchemy 3.0.5
- **Server**: Gunicorn 22.0.0
- **Containerization**: Docker & Docker Compose
- **Testing**: Selenium WebDriver
- **CI/CD**: Jenkins
- **Admin Panel**: pgAdmin 4
- **Language**: Python 3.9

## Project Structure

```
resume_builder/
├── app.py                          # Main Flask application
├── automation.py                   # Selenium-based automated testing
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image configuration
├── docker-compose.yml              # Multi-container Docker setup
├── Jenkinsfile                     # CI/CD pipeline configuration
├── README.md                       # Project documentation
├── resume_builder.db               # SQLite database (development)
├── config/
│   └── postgres.env               # PostgreSQL environment variables
├── migrations/                     # Database migration scripts
├── static/
│   ├── css/
│   │   └── style.css              # Main stylesheet
│   ├── images/                     # Static images
│   └── js/
│       └── script.js               # Frontend JavaScript
└── templates/
    ├── index.html                  # Landing page
    ├── login.html                  # Login page
    ├── register.html               # Registration page
    ├── dashboard.html              # User dashboard
    ├── add_resume.html             # Resume basic info form
    ├── work_experience.html        # Work experience form
    ├── education.html              # Education form
    ├── skills.html                 # Skills form
    ├── add_languages.html          # Languages form
    ├── achievements.html           # Achievements form
    └── generated_resume.html       # Resume preview/download page
```

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 13+ (for production)
- Git
- Chrome/Chromium browser (for Selenium testing)
- ChromeDriver (for Selenium testing)

## Installation

### Clone the Repository

```bash
git clone https://github.com/akhilasuresh02/resume_builder.git
cd resume_builder
```

### Install Dependencies (Local Development)

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your_secure_secret_key_here

# Database Configuration (for PostgreSQL)
DB_NAME=resume_db
DB_USER=myuser
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Application Settings
DEBUG=True
```

### Database Setup

The application automatically creates SQLite tables on first run if using SQLite. For PostgreSQL, ensure the database and user are created before starting:

```sql
CREATE DATABASE resume_db;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE resume_db TO myuser;
```

## Running the Application

### Local Development (SQLite)

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the Flask application
python app.py
```

The application will start on `http://localhost:5000`

### Docker Deployment (PostgreSQL + Flask + pgAdmin)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services running:**
- **Web Application**: http://localhost:5000
- **PostgreSQL Database**: localhost:5432
- **pgAdmin (Database UI)**: http://localhost:5055
  - Email: 22bcaf07@kristujayanti.com
  - Password: ADMIN

## Usage Guide

### User Registration and Login

1. Navigate to the landing page
2. Click "Get Started"
3. Click "Register Here" to create a new account
4. Enter username, email, and password
5. Successfully registered users are redirected to login
6. Log in with email and password

### Creating a Resume

1. After login, click "Add Resume" on your dashboard
2. Fill in your personal information (name, summary, email, phone)
3. Click "Next" to proceed to work experience
4. Add your work experiences
5. Continue through each step:
   - Work Experience
   - Skills
   - Education
   - Languages
   - Achievements
6. Review and generate your professional resume

### Viewing and Downloading

- Access your generated resume from the dashboard
- Print or download the resume directly from your browser

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
```

### Resumes Table
```sql
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    summary TEXT,
    email TEXT,
    phone TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Skills Table
```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER,
    skill_name TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET, POST | `/login` | User login |
| GET, POST | `/register` | User registration |
| GET | `/dashboard` | User dashboard |
| GET, POST | `/add_resume` | Create/edit resume |
| GET, POST | `/work-experience` | Add work experience |
| GET, POST | `/add_skills` | Add skills |
| GET, POST | `/education` | Add education |
| GET, POST | `/add_languages` | Add languages |
| GET, POST | `/achievements` | Add achievements |
| GET | `/generated_resume` | View generated resume |

## Automation Testing

The project includes Selenium-based automated testing in `automation.py`.

### Setup

1. Install ChromeDriver matching your Chrome version
2. Install Selenium dependencies (included in requirements.txt)

### Running Tests

```bash
# Ensure the Flask application is running
python app.py

# In another terminal, run the automation tests
python automation.py
```

### What the Tests Do

- Navigate to landing page
- Click "Get Started" button
- Register a new user with test credentials
- Log in with registered credentials
- Add a resume with sample data
- Navigate through the resume builder steps

## CI/CD Pipeline

The project uses Jenkins for continuous integration and deployment. The Jenkinsfile defines a pipeline with the following stages:

### Pipeline Stages

1. **Checkout**: Clones the code from the GitHub repository
2. **Build**: Builds Docker Compose services
3. **Test**: Runs automated tests (currently skipped)
4. **Deploy**: Deploys the application using Docker Compose

### Triggering the Pipeline

The pipeline is configured to work with the repository: `https://github.com/akhilasuresh02/resume_builder.git`

Ensure Jenkins has:
- Docker installed
- Git credentials configured
- `resumeid` credential ID set up for GitHub access

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

#### Database Connection Error

```bash
# Verify database is running
docker-compose ps

# Restart database service
docker-compose restart db
```

#### Chrome Driver Issues (Testing)

```bash
# Download ChromeDriver matching your Chrome version
# Place it in your system PATH or specify path in automation.py
```

#### Permission Denied on Docker

```bash
# On Linux, add your user to docker group
sudo usermod -aG docker $USER
sudo systemctl restart docker
```

### Debug Mode

Set `DEBUG=True` in `.env` or uncomment in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

This enables:
- Flask debugger on errors
- Auto-reload on file changes
- Detailed error pages

## Security Considerations

- **Passwords**: Always use strong, unique passwords
- **Secret Key**: Change the `SECRET_KEY` in production
- **Environment Variables**: Keep sensitive data in `.env` files (never commit to version control)
- **pgAdmin Credentials**: Change default pgAdmin password
- **HTTPS**: Use HTTPS in production environments
- **SQL Injection**: Application uses parameterized queries for protection

## Future Enhancements

- Resume template selection
- PDF export functionality
- Resume sharing and collaboration
- ATS-optimized resume format
- Multi-language support
- Email notifications
- Resume analytics
- LinkedIn integration
- Real-time preview

## Support

For issues, questions, or suggestions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## License

This project is open source and available under the MIT License.

## Author

**Akhila Suresh**
- GitHub: [@akhilasuresh02](https://github.com/akhilasuresh02)
- Email: akhilasuresh1937@gmail.com

---

**Last Updated**: April 2026

**Version**: 1.0.0

For the most recent updates, visit the [GitHub Repository](https://github.com/akhilasuresh02/resume_builder)
