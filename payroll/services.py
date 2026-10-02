from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from .models import SalaryStructure, Payroll
from attendance.models import Attendance, OvertimeRequest, Leave
from accounts.models import EmployeeProfile


def calculate_payable_days(employee, month, year):
    """Calculate payable days based on finalized attendance and approved leaves."""
    # Get first and last day of month
    if month == 12:
        first_day = date(year, month, 1)
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        first_day = date(year, month, 1)
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get finalized attendance for the month
    attendances = Attendance.objects.filter(
        employee=employee,
        date__range=[first_day, last_day],
        is_finalized=True
    )
    
    payable_days = 0
    
    for attendance in attendances:
        if attendance.status in ['PRESENT', 'LATE']:
            payable_days += 1
        elif attendance.status == 'HALF_DAY':
            payable_days += 0.5
    
    # Add approved paid leave days
    approved_leaves = Leave.objects.filter(
        employee=employee,
        start_date__lte=last_day,
        end_date__gte=first_day,
        status='APPROVED',
        leave_type__in=['PAID', 'CASUAL', 'SICK']
    )
    
    for leave in approved_leaves:
        # Calculate overlap with month
        overlap_start = max(leave.start_date, first_day)
        overlap_end = min(leave.end_date, last_day)
        leave_days = (overlap_end - overlap_start).days + 1
        payable_days += leave_days
    
    return payable_days


def calculate_unpaid_leave_days(employee, month, year):
    """Calculate unpaid leave days for deduction."""
    if month == 12:
        first_day = date(year, month, 1)
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        first_day = date(year, month, 1)
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    unpaid_leaves = Leave.objects.filter(
        employee=employee,
        start_date__lte=last_day,
        end_date__gte=first_day,
        status='APPROVED',
        leave_type='UNPAID'
    )
    
    unpaid_days = 0
    for leave in unpaid_leaves:
        overlap_start = max(leave.start_date, first_day)
        overlap_end = min(leave.end_date, last_day)
        leave_days = (overlap_end - overlap_start).days + 1
        unpaid_days += leave_days
    
    return unpaid_days


def calculate_approved_overtime_hours(employee, month, year):
    """Calculate total approved overtime hours for the month."""
    if month == 12:
        first_day = date(year, month, 1)
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        first_day = date(year, month, 1)
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    approved_overtime = OvertimeRequest.objects.filter(
        employee=employee,
        attendance__date__range=[first_day, last_day],
        status='APPROVED'
    )
    
    total_hours = sum(overtime.hours for overtime in approved_overtime)
    return total_hours


def generate_payroll(employee, month, year):
    """Generate payroll for an employee for a given month and year."""
    # Get or create salary structure
    try:
        # Calculate last day of the month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        salary_structure = SalaryStructure.objects.filter(
            employee=employee,
            effective_from__lte=last_day
        ).order_by('-effective_from').first()
    except Exception as e:
        print(f"Error fetching salary structure for {employee.full_name}: {e}")
        return None
    
    if not salary_structure:
        print(f"No salary structure found for {employee.full_name} for month {month}/{year}")
        return None
    
    # Calculate components
    payable_days = calculate_payable_days(employee, month, year)
    unpaid_leave_days = calculate_unpaid_leave_days(employee, month, year)
    approved_overtime_hours = calculate_approved_overtime_hours(employee, month, year)
    
    # Standard working days in a month (26)
    standard_working_days = 26
    
    # Calculate gross salary
    basic_salary = salary_structure.basic_salary
    hra = salary_structure.hra
    transport_allowance = salary_structure.transport_allowance
    other_allowance = salary_structure.other_allowance
    
    # Calculate overtime pay
    # Hourly rate = basic_salary / (standard_working_days * 8)
    hourly_rate = basic_salary / Decimal(standard_working_days * 8)
    overtime_multiplier = Decimal('1.5')
    overtime_pay = hourly_rate * Decimal(approved_overtime_hours) * overtime_multiplier
    
    # Total allowances
    total_allowances = hra + transport_allowance + other_allowance
    
    # Gross salary
    gross_salary = basic_salary + total_allowances + overtime_pay
    
    # Calculate leave deduction
    daily_salary = basic_salary / Decimal(standard_working_days)
    leave_deduction = daily_salary * Decimal(unpaid_leave_days)
    
    # Calculate deductions
    pf_deduction = basic_salary * (salary_structure.pf_percentage / 100)
    tax_deduction = gross_salary * (salary_structure.tax_percentage / 100)
    
    # Total deductions
    total_deductions = pf_deduction + tax_deduction + leave_deduction
    
    # Net salary
    net_salary = gross_salary - total_deductions
    
    # Create or update payroll record
    payroll, created = Payroll.objects.update_or_create(
        employee=employee,
        month=month,
        year=year,
        defaults={
            'basic_salary': basic_salary,
            'allowances': total_allowances,
            'gross_salary': gross_salary,
            'payable_days': payable_days,
            'leave_deduction': leave_deduction,
            'overtime_pay': overtime_pay,
            'pf_deduction': pf_deduction,
            'tax_deduction': tax_deduction,
            'total_deductions': total_deductions,
            'net_salary': net_salary,
            'status': 'DRAFT'
        }
    )
    
    return payroll
