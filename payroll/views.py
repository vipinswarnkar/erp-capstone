from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO
from decimal import Decimal
from .models import SalaryStructure, Payroll
from .forms import SalaryStructureForm, PayrollRunForm
from .services import generate_payroll
from accounts.models import EmployeeProfile


@login_required
def payroll_list(request):
    user_profile = request.user.employee_profile
    
    if user_profile.role == 'HR':
        payrolls = Payroll.objects.select_related('employee').all().order_by('-year', '-month')
    else:
        payrolls = Payroll.objects.filter(employee=user_profile).order_by('-year', '-month')
    
    context = {
        'payrolls': payrolls,
    }
    return render(request, 'payroll/payroll_list.html', context)


# HR Salary Structure Management

@login_required
def hr_salary_structure_list(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    structures = SalaryStructure.objects.select_related('employee').all().order_by('-effective_from')
    
    context = {
        'structures': structures,
    }
    return render(request, 'payroll/hr_salary_structure_list.html', context)


@login_required
def hr_salary_structure_create(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary structure created successfully.')
            return redirect('hr_salary_structure_list')
    else:
        form = SalaryStructureForm()
    
    context = {
        'form': form,
    }
    return render(request, 'payroll/hr_salary_structure_create.html', context)


@login_required
def hr_salary_structure_edit(request, structure_id):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    structure = get_object_or_404(SalaryStructure, pk=structure_id)
    
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST, instance=structure)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary structure updated successfully.')
            return redirect('hr_salary_structure_list')
    else:
        form = SalaryStructureForm(instance=structure)
    
    context = {
        'form': form,
        'structure': structure,
    }
    return render(request, 'payroll/hr_salary_structure_edit.html', context)


# HR Payroll Management

@login_required
def hr_payroll_run(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PayrollRunForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data['month'])
            year = int(form.cleaned_data['year'])
            
            # Get all active employees
            employees = EmployeeProfile.objects.filter(is_active=True)
            print(f"Found {employees.count()} active employees")
            
            generated_count = 0
            skipped_count = 0
            for employee in employees:
                print(f"Processing employee: {employee.full_name} (ID: {employee.id})")
                payroll = generate_payroll(employee, month, year)
                if payroll:
                    generated_count += 1
                else:
                    skipped_count += 1
            
            messages.success(request, f'Payroll generated for {generated_count} employees. Skipped: {skipped_count}.')
            return redirect('hr_payroll_list')
    else:
        form = PayrollRunForm()
    
    context = {
        'form': form,
    }
    return render(request, 'payroll/hr_payroll_run.html', context)


@login_required
def hr_payroll_list(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    payrolls = Payroll.objects.select_related('employee').all().order_by('-year', '-month')
    
    context = {
        'payrolls': payrolls,
    }
    return render(request, 'payroll/hr_payroll_list.html', context)


@login_required
def hr_payroll_approve(request, payroll_id):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    payroll = get_object_or_404(Payroll, pk=payroll_id)
    
    if payroll.status == 'LOCKED':
        messages.error(request, 'Payroll is already locked.')
        return redirect('hr_payroll_list')
    
    payroll.status = 'APPROVED'
    payroll.save()
    
    messages.success(request, 'Payroll approved successfully.')
    return redirect('hr_payroll_list')


@login_required
def hr_payroll_lock(request, payroll_id):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    payroll = get_object_or_404(Payroll, pk=payroll_id)
    
    if payroll.status != 'APPROVED':
        messages.error(request, 'Payroll must be approved before locking.')
        return redirect('hr_payroll_list')
    
    payroll.status = 'LOCKED'
    payroll.save()
    
    # Generate payslip PDF
    generate_payslip_pdf(payroll)
    
    messages.success(request, 'Payroll locked and payslip generated.')
    return redirect('hr_payroll_list')


def generate_payslip_pdf(payroll):
    """Generate payslip PDF using ReportLab."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, 10 * inch, "Payslip")
    
    # Company info (placeholder)
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, 9.5 * inch, "Company Name")
    p.drawString(1 * inch, 9.3 * inch, "Address Line 1")
    p.drawString(1 * inch, 9.1 * inch, "City, State, Zip")
    
    # Employee info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, 8.5 * inch, "Employee Details")
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, 8.2 * inch, f"Name: {payroll.employee.full_name}")
    p.drawString(1 * inch, 8.0 * inch, f"Employee ID: {payroll.employee.employee_id}")
    p.drawString(1 * inch, 7.8 * inch, f"Department: {payroll.employee.department}")
    p.drawString(1 * inch, 7.6 * inch, f"Designation: {payroll.employee.designation}")
    p.drawString(1 * inch, 7.4 * inch, f"Pay Period: {payroll.month}/{payroll.year}")
    
    # Earnings
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, 6.8 * inch, "Earnings")
    p.setFont("Helvetica", 10)
    y_pos = 6.5 * inch
    p.drawString(1 * inch, y_pos, f"Basic Salary: {payroll.basic_salary:.2f}")
    y_pos -= 0.2 * inch
    p.drawString(1 * inch, y_pos, f"HRA: {payroll.allowances * Decimal('0.4'):.2f}")  # Approximate split
    y_pos -= 0.2 * inch
    p.drawString(1 * inch, y_pos, f"Transport Allowance: {payroll.allowances * Decimal('0.3'):.2f}")
    y_pos -= 0.2 * inch
    p.drawString(1 * inch, y_pos, f"Other Allowance: {payroll.allowances * Decimal('0.3'):.2f}")
    y_pos -= 0.2 * inch
    p.drawString(1 * inch, y_pos, f"Overtime Pay: {payroll.overtime_pay:.2f}")
    y_pos -= 0.2 * inch
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1 * inch, y_pos, f"Gross Salary: {payroll.gross_salary:.2f}")
    
    # Deductions
    y_pos -= 0.4 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, y_pos, "Deductions")
    p.setFont("Helvetica", 10)
    y_pos -= 0.2 * inch
    p.drawString(1 * inch, y_pos, f"PF: {payroll.pf_deduction:.2f}")
    y_pos -= 0.2 * inch
    p.drawString(1 * inch, y_pos, f"Tax: {payroll.tax_deduction:.2f}")
    y_pos -= 0.2 * inch
    p.drawString(1 * inch, y_pos, f"Leave Deduction: {payroll.leave_deduction:.2f}")
    y_pos -= 0.2 * inch
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1 * inch, y_pos, f"Total Deductions: {payroll.total_deductions:.2f}")
    
    # Net Salary
    y_pos -= 0.4 * inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, y_pos, f"NET SALARY: {payroll.net_salary:.2f}")
    
    p.save()
    
    # Save to payroll record
    buffer.seek(0)
    filename = f"payslip_{payroll.employee.employee_id}_{payroll.month}_{payroll.year}.pdf"
    payroll.payslip_file.save(filename, buffer)
    payroll.save()
