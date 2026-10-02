# ERP Attendance and Payroll System - Project Report

## Project Overview

This ERP system is a comprehensive web-based application built with Django 5.x that manages employee attendance, shift scheduling, leave management, and payroll processing. The system provides role-based access control for Employees, Managers, and HR personnel.

## Technology Stack

- **Backend Framework**: Django 5.2.5
- **Frontend**: Bootstrap 5.3.0
- **Database**: SQLite (development)
- **PDF Generation**: ReportLab
- **Python Version**: 3.12
- **Authentication**: Django's built-in authentication system

## Project Structure

```
ERP/
├── config/                 # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/              # Authentication and user management
│   ├── models.py         # EmployeeProfile model
│   ├── views.py          # Login, logout, dashboard views
│   ├── forms.py          # User and employee forms
│   └── urls.py
├── attendance/           # Attendance and shift management
│   ├── models.py         # Shift, Attendance, Leave, Correction, Overtime models
│   ├── views.py          # Attendance, shift, correction, overtime views
│   ├── forms.py          # Attendance-related forms
│   └── urls.py
├── payroll/              # Payroll processing
│   ├── models.py         # SalaryStructure, Payroll models
│   ├── views.py          # Payroll generation, payslip views
│   ├── services.py       # Payroll calculation logic
│   ├── forms.py          # Payroll forms
│   └── urls.py
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── accounts/         # Account-related templates
│   ├── attendance/       # Attendance-related templates
│   └── payroll/          # Payroll-related templates
├── static/               # Static files (CSS, JS)
├── media/                # Media files (payslips)
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## Core Features

### 1. Authentication & User Management

- **User Roles**: EMPLOYEE, MANAGER, HR
- **Employee Profile**: Extended Django User model with employee details
- **HR Employee Management**: HR can create, view, and edit employee records
- **Role-Based Access Control**: Different dashboards and permissions per role

### 2. Shift Management

- **Shift Creation**: Define shift timings, grace periods, and working hours
- **Shift Assignment**: Assign shifts to employees with effective dates
- **Shift History**: Track shift assignments over time
- **Active/Inactive Shifts**: Enable or disable shifts as needed

### 3. Attendance System

- **Check-In/Check-Out**: Employees can check in and check out based on assigned shifts
- **Late Detection**: Automatic late detection based on shift start time and grace period
- **Attendance History**: View attendance records with status, working hours, and overtime
- **HR Finalization**: HR can finalize attendance records for payroll processing

### 4. Attendance Corrections

- **Correction Requests**: Employees can request corrections to check-in/check-out times
- **Manager Approval**: Managers review and approve/reject correction requests
- **Automatic Updates**: Approved corrections automatically update attendance records
- **Status Tracking**: Track correction request status (PENDING, APPROVED, REJECTED)

### 5. Overtime Management

- **Overtime Requests**: Employees can request overtime approval
- **Manager Approval**: Managers review and approve/reject overtime requests
- **Overtime Calculation**: Automatic overtime calculation based on working hours
- **Payroll Integration**: Approved overtime included in payroll calculation

### 6. Leave Management

- **Leave Types**: CASUAL, SICK, PAID, UNPAID
- **Leave Requests**: HR can create leave records for employees
- **Leave Status**: PENDING, APPROVED, REJECTED
- **Leave Impact**: Paid leaves included in payable days, unpaid leaves deducted
- **Leave Duration**: Automatic calculation of leave days

### 7. Payroll System

- **Salary Structures**: Define salary components (basic, HRA, transport, other allowances)
- **PF & Tax Configuration**: Configure PF and tax percentages per employee
- **Payroll Generation**: Batch payroll generation for all active employees
- **Payroll Calculation**: Automatic calculation of gross salary, deductions, and net salary
- **Payslip Generation**: PDF payslip generation with detailed breakdown
- **Payroll Workflow**: DRAFT → APPROVED → LOCKED status flow

## Database Models

### EmployeeProfile
- employee_id (unique)
- full_name
- email
- department
- designation
- date_of_joining
- role (EMPLOYEE/MANAGER/HR)
- is_active

### Shift
- name
- start_time
- end_time
- grace_period_minutes
- working_hours
- is_active

### EmployeeShift
- employee (FK)
- shift (FK)
- effective_from
- effective_to

### Attendance
- employee (FK)
- date
- shift (FK)
- check_in
- check_out
- status (PRESENT/LATE/ABSENT/LEAVE/HALF_DAY)
- working_hours
- late_minutes
- overtime_hours
- is_finalized

### AttendanceCorrection
- employee (FK)
- attendance (FK)
- requested_check_in
- requested_check_out
- reason
- status (PENDING/APPROVED/REJECTED)
- manager_comment

### OvertimeRequest
- employee (FK)
- attendance (FK)
- hours
- reason
- status (PENDING/APPROVED/REJECTED)
- manager_comment

### Leave
- employee (FK)
- start_date
- end_date
- leave_type (CASUAL/SICK/PAID/UNPAID)
- reason
- status (PENDING/APPROVED/REJECTED)

### SalaryStructure
- employee (FK)
- basic_salary
- hra
- transport_allowance
- other_allowance
- pf_percentage
- tax_percentage
- effective_from

### Payroll
- employee (FK)
- month
- year
- basic_salary
- allowances
- gross_salary
- payable_days
- leave_deduction
- overtime_pay
- pf_deduction
- tax_deduction
- total_deductions
- net_salary
- status (DRAFT/APPROVED/LOCKED)
- payslip_file

## Attendance Flow

![Attendance Flow](attendance_flow.png)

**Attendance Workflow:**
1. HR creates shifts and assigns them to employees
2. Employee logs in and views assigned shift
3. Employee checks in (system records time and calculates status)
4. Employee checks out (system calculates working hours and overtime)
5. If needed, employee requests corrections to check-in/out times
6. Manager reviews and approves/rejects correction requests
7. If overtime worked, employee requests overtime approval
8. Manager reviews and approves/rejects overtime requests
9. HR finalizes attendance records for payroll processing

## Payment Flow

![Payment Flow](payment_flow.png)

**Payroll Workflow:**
1. HR creates salary structures for employees
2. HR runs payroll for a specific month/year
3. System calculates:
   - Payable days (based on finalized attendance + approved leaves)
   - Unpaid leave days (for deduction)
   - Approved overtime hours
   - Basic salary + allowances + overtime pay
   - PF deduction, tax deduction, leave deduction
   - Net salary
4. HR reviews and approves payroll
5. HR locks payroll (generates PDF payslip)
6. Employees can view and download their payslips

## Payroll Calculation Logic

### Payable Days Calculation
- Count of finalized attendance with status PRESENT or LATE = 1 day each
- Count of finalized attendance with status HALF_DAY = 0.5 day each
- Add approved paid leave days (CASUAL, SICK, PAID)

### Unpaid Leave Calculation
- Count of approved UNPAID leave days

### Overtime Calculation
- Sum of approved overtime hours for the month

### Gross Salary
```
Basic Salary + HRA + Transport Allowance + Other Allowance + Overtime Pay
```

### Overtime Pay
```
Hourly Rate = Basic Salary / (Standard Working Days × 8)
Overtime Pay = Hourly Rate × Overtime Hours × 1.5
```

### Deductions
```
PF Deduction = Basic Salary × PF Percentage
Tax Deduction = Gross Salary × Tax Percentage
Leave Deduction = Daily Salary × Unpaid Leave Days
Total Deductions = PF + Tax + Leave Deduction
```

### Net Salary
```
Net Salary = Gross Salary - Total Deductions
```

## User Roles & Permissions

### Employee
- View dashboard
- Check-in/Check-out
- View attendance history
- Request attendance corrections
- Request overtime approval
- View/download payslips

### Manager
- View dashboard
- Review pending correction requests
- Approve/reject corrections
- Review pending overtime requests
- Approve/reject overtime

### HR
- View dashboard
- Create/edit employees
- Create/edit shifts
- Assign shifts to employees
- View/finalize attendance
- Manage leave records
- Create/edit salary structures
- Run payroll
- Approve/lock payroll
- Generate payslips

## Security Features

- Role-based access control
- Login required for all views
- HR-only access to sensitive operations
- Manager-only access to approval workflows
- Employee-only access to personal data
- Session-based authentication

## Deployment Considerations

### Production Checklist
- Change database from SQLite to PostgreSQL/MySQL
- Set DEBUG = False in settings
- Configure ALLOWED_HOSTS
- Use production WSGI server (Gunicorn/uWSGI)
- Configure static files serving
- Set up media file storage (AWS S3/CloudFront)
- Enable HTTPS
- Configure CORS if needed
- Set up logging
- Configure email backend for notifications

### Environment Variables
- SECRET_KEY
- DATABASE_URL
- DEBUG
- ALLOWED_HOSTS
- MEDIA_ROOT
- STATIC_ROOT

## Future Enhancements

- Email notifications for approvals
- Mobile app for check-in/check-out
- Biometric attendance integration
- Advanced reporting and analytics
- Multi-company support
- Integration with accounting software
- Leave balance tracking
- Holiday calendar management
- Timesheet approval workflow
- Expense management module
- Performance review integration

## Testing Recommendations

- Unit tests for payroll calculation logic
- Integration tests for attendance workflow
- Role-based access control tests
- Form validation tests
- API endpoint tests (if REST API added)
- Performance testing for payroll generation
- Security testing for authorization

## Conclusion

This ERP system provides a complete solution for attendance and payroll management with role-based access control, automated calculations, and PDF payslip generation. The system is designed to be scalable and can be extended with additional features as needed.

---

**Project Status**: ✅ Complete

**Last Updated**: August 11, 2026
