# ERP System Setup Guide

## Initial Setup

### 1. Create Superuser (HR/Admin)

Run the following command to create the initial HR admin user:

```bash
python manage.py createsuperuser
```

Enter the following details:
- Username: admin
- Email: admin@company.com
- Password: [your password]

### 2. Create Initial Data via Django Admin

After creating the superuser, access the admin panel at http://127.0.0.1:8000/admin/

#### Step 1: Create Shifts
Navigate to Attendance → Shifts and create:
- **Morning Shift**: 09:00 - 18:00, Grace: 15 mins, Working Hours: 8.0
- **Night Shift**: 20:00 - 05:00, Grace: 15 mins, Working Hours: 8.0

#### Step 2: Create HR User
Navigate to Authentication and Authorization → Users:
1. Create a new user with HR role
2. Go to Employee Profiles and create the profile:
   - Employee ID: HR001
   - Full Name: HR Admin
   - Email: hr@company.com
   - Department: HR
   - Designation: HR Manager
   - Date of Joining: [current date]
   - Role: HR
   - Is Active: Yes

#### Step 3: Create Sample Employees
Create a few sample employees:
- **Manager**: EMP001, John Manager, role: MANAGER
- **Employee**: EMP002, Jane Employee, role: EMPLOYEE

#### Step 4: Assign Shifts
Navigate to Attendance → Employee Shifts and assign shifts to employees.

#### Step 5: Create Salary Structures
Navigate to Payroll → Salary Structures and create salary structures for employees.

### 3. Run the Development Server

```bash
python manage.py runserver
```

Access the application at http://127.0.0.1:8000/

## User Login URLs

- **Login**: http://127.0.0.1:8000/login/
- **Employee Dashboard**: http://127.0.0.1:8000/dashboard/
- **HR Dashboard**: http://127.0.0.1:8000/dashboard/ (after login as HR)
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Typical Workflow

### Employee Workflow
1. Login with employee credentials
2. Check-in for the day (if shift assigned)
3. Check-out at end of day
4. View attendance history
5. Submit correction requests if needed
6. Submit overtime requests if applicable
7. View/download payslips when available

### Manager Workflow
1. Login with manager credentials
2. Review pending correction requests
3. Approve/reject corrections
4. Review pending overtime requests
5. Approve/reject overtime

### HR Workflow
1. Login with HR credentials
2. Create and manage employees
3. Create and manage shifts
4. Assign shifts to employees
5. View and finalize attendance
6. Manage leave records
7. Create salary structures
8. Run monthly payroll
9. Approve and lock payroll
10. Generate payslips

## Database

The SQLite database file is located at `db.sqlite3` in the project root.

## Static and Media Files

- **Static files**: `static/` directory (CSS, JS)
- **Media files**: `media/` directory (payslips)

## Troubleshooting

### Migration Issues
If you encounter migration issues, run:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
Ensure static directories exist:
```bash
static/css/
static/js/
```

### Payslip Generation Issues
Ensure the `media/payslips/` directory exists and is writable.
