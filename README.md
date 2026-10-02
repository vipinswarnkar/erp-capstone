# ERP-Driven Attendance and Payroll Management System

A Django-based ERP system for managing employee attendance and payroll.

## Technology Stack

- Python 3.x
- Django 5.x
- SQLite
- Bootstrap 5
- ReportLab (for PDF generation)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
erp_project/
├── manage.py
├── config/              # Django project configuration
├── accounts/           # User authentication and profiles
├── attendance/         # Attendance management
├── payroll/           # Payroll calculations
├── templates/          # HTML templates
├── static/            # Static files
└── media/             # Media files (payslips)
```

## User Roles

- **Employee**: Can check in/out, view attendance, submit correction requests
- **Manager**: Can approve corrections and overtime requests
- **HR/Admin**: Can manage employees, shifts, salary structures, and run payroll

## Features

- Employee management
- Shift assignment
- Daily attendance tracking (check-in/check-out)
- Late marking with grace periods
- Attendance correction requests
- Overtime calculation and approval
- Leave management
- Monthly payroll calculation
- Payslip PDF generation

## Access

- Login page: http://127.0.0.1:8000/login/
- Admin panel: http://127.0.0.1:8000/admin/
