from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date, timedelta
from .models import Attendance, AttendanceCorrection, OvertimeRequest, Shift, EmployeeShift, Leave
from accounts.models import EmployeeProfile
from .forms import ShiftForm, EmployeeShiftForm, AttendanceCorrectionForm, OvertimeRequestForm, LeaveForm


@login_required
def attendance_today(request):
    employee = request.user.employee_profile
    today = date.today()
    
    try:
        attendance = Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        attendance = None
    
    # Get current shift - check all assignments
    current_shift = EmployeeShift.objects.filter(
        employee=employee,
        effective_from__lte=today
    ).order_by('-effective_from').first()
    
    shift = None
    if current_shift:
        # Check if assignment is still valid
        if current_shift.effective_to is None or current_shift.effective_to >= today:
            shift = current_shift.shift
        else:
            # Assignment expired
            messages.warning(request, f'Your shift assignment expired on {current_shift.effective_to}. Please contact HR.')
    
    if not shift:
        # Check if there are any future assignments
        future_shift = EmployeeShift.objects.filter(
            employee=employee,
            effective_from__gt=today
        ).order_by('effective_from').first()
        if future_shift:
            messages.info(request, f'You have a shift assignment starting from {future_shift.effective_from}.')
    
    context = {
        'attendance': attendance,
        'shift': shift,
        'today': today,
    }
    return render(request, 'attendance/attendance_today.html', context)


@login_required
def check_in(request):
    employee = request.user.employee_profile
    today = date.today()
    now = timezone.now()
    
    # Check if already checked in
    if Attendance.objects.filter(employee=employee, date=today).exists():
        messages.error(request, 'You have already checked in today.')
        return redirect('attendance_today')
    
    # Get current shift
    try:
        current_shift = EmployeeShift.objects.filter(
            employee=employee,
            effective_from__lte=today
).order_by('-effective_from').first()
        if not current_shift or (current_shift.effective_to and current_shift.effective_to < today):
            messages.error(request, 'No active shift assigned. Please contact HR.')
            return redirect('attendance_today')
        
        shift = current_shift.shift
    except:
        messages.error(request, 'No shift assigned. Please contact HR.')
        return redirect('attendance_today')
    
    # Determine status based on check-in time
    shift_start = datetime.combine(today, shift.start_time)
    # Make timezone-aware
    from django.utils.timezone import make_aware
    shift_start = make_aware(shift_start)
    grace_period_end = shift_start.replace(minute=shift_start.minute + shift.grace_period_minutes)
    
    status = 'PRESENT'
    late_minutes = 0
    
    if now > grace_period_end:
        status = 'LATE'
        late_minutes = int((now - shift_start).total_seconds() / 60)
    
    # Create attendance record
    attendance = Attendance.objects.create(
        employee=employee,
        date=today,
        shift=shift,
        check_in=now,
        status=status,
        late_minutes=late_minutes
    )
    
    messages.success(request, f'Checked in successfully at {now.strftime("%H:%M")}. Status: {status}')
    return redirect('attendance_today')


@login_required
def check_out(request):
    employee = request.user.employee_profile
    today = date.today()
    now = timezone.now()
    
    try:
        attendance = Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, 'No check-in record found for today.')
        return redirect('attendance_today')
    
    if attendance.check_out:
        messages.error(request, 'You have already checked out today.')
        return redirect('attendance_today')
    
    # Record check-out
    attendance.check_out = now
    
    # Calculate working hours
    if attendance.check_in:
        duration = now - attendance.check_in
        attendance.working_hours = round(duration.total_seconds() / 3600, 2)
        
        # Calculate overtime
        if attendance.shift:
            standard_hours = attendance.shift.working_hours
            if attendance.working_hours > standard_hours:
                attendance.overtime_hours = round(attendance.working_hours - standard_hours, 2)
    
    attendance.save()
    
    messages.success(request, f'Checked out successfully at {now.strftime("%H:%M")}. Working hours: {attendance.working_hours}')
    return redirect('attendance_today')


# HR Shift Management Views

@login_required
def hr_shift_list(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    shifts = Shift.objects.all().order_by('-created_at')
    context = {
        'shifts': shifts,
    }
    return render(request, 'attendance/hr_shift_list.html', context)


@login_required
def hr_shift_create(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift created successfully.')
            return redirect('hr_shift_list')
    else:
        form = ShiftForm()
    
    context = {
        'form': form,
    }
    return render(request, 'attendance/hr_shift_create.html', context)


@login_required
def hr_shift_edit(request, shift_id):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    shift = get_object_or_404(Shift, pk=shift_id)
    
    if request.method == 'POST':
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift updated successfully.')
            return redirect('hr_shift_list')
    else:
        form = ShiftForm(instance=shift)
    
    context = {
        'form': form,
        'shift': shift,
    }
    return render(request, 'attendance/hr_shift_edit.html', context)


@login_required
def hr_shift_assignment_list(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    assignments = EmployeeShift.objects.select_related('employee', 'shift').all().order_by('-effective_from')
    context = {
        'assignments': assignments,
    }
    return render(request, 'attendance/hr_shift_assignment_list.html', context)


@login_required
def hr_shift_assignment_create(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmployeeShiftForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift assigned successfully.')
            return redirect('hr_shift_assignment_list')
    else:
        form = EmployeeShiftForm()
    
    context = {
        'form': form,
    }
    return render(request, 'attendance/hr_shift_assignment_create.html', context)


# Employee Attendance History

@login_required
def attendance_history(request):
    employee = request.user.employee_profile
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')
    
    context = {
        'attendances': attendances,
    }
    return render(request, 'attendance/attendance_history.html', context)


# HR Attendance Management

@login_required
def hr_attendance_list(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    attendances = Attendance.objects.select_related('employee', 'shift').all().order_by('-date')
    
    context = {
        'attendances': attendances,
    }
    return render(request, 'attendance/hr_attendance_list.html', context)


@login_required
def hr_attendance_finalize(request, attendance_id):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    
    if attendance.is_finalized:
        messages.warning(request, 'Attendance is already finalized.')
        return redirect('hr_attendance_list')
    
    attendance.is_finalized = True
    attendance.save()
    
    messages.success(request, 'Attendance finalized successfully.')
    return redirect('hr_attendance_list')


# Employee Correction Requests

@login_required
def correction_request_list(request):
    employee = request.user.employee_profile
    corrections = AttendanceCorrection.objects.filter(employee=employee).order_by('-created_at')
    
    context = {
        'corrections': corrections,
    }
    return render(request, 'attendance/correction_request_list.html', context)


@login_required
def correction_request_create(request, attendance_id):
    employee = request.user.employee_profile
    attendance = get_object_or_404(Attendance, pk=attendance_id, employee=employee)
    
    # Check if already has pending correction
    if AttendanceCorrection.objects.filter(attendance=attendance, status='PENDING').exists():
        messages.error(request, 'You already have a pending correction request for this attendance.')
        return redirect('correction_request_list')
    
    if request.method == 'POST':
        form = AttendanceCorrectionForm(request.POST)
        if form.is_valid():
            correction = form.save(commit=False)
            correction.employee = employee
            correction.attendance = attendance
            correction.save()
            messages.success(request, 'Correction request submitted successfully.')
            return redirect('correction_request_list')
    else:
        form = AttendanceCorrectionForm()
    
    context = {
        'form': form,
        'attendance': attendance,
    }
    return render(request, 'attendance/correction_request_create.html', context)


# Employee Overtime Requests

@login_required
def overtime_request_list(request):
    employee = request.user.employee_profile
    overtime_requests = OvertimeRequest.objects.filter(employee=employee).order_by('-created_at')
    
    context = {
        'overtime_requests': overtime_requests,
    }
    return render(request, 'attendance/overtime_request_list.html', context)


@login_required
def overtime_request_create(request, attendance_id):
    employee = request.user.employee_profile
    attendance = get_object_or_404(Attendance, pk=attendance_id, employee=employee)
    
    # Check if already has pending overtime request
    if OvertimeRequest.objects.filter(attendance=attendance, status='PENDING').exists():
        messages.error(request, 'You already have a pending overtime request for this attendance.')
        return redirect('overtime_request_list')
    
    if request.method == 'POST':
        form = OvertimeRequestForm(request.POST)
        if form.is_valid():
            overtime = form.save(commit=False)
            overtime.employee = employee
            overtime.attendance = attendance
            overtime.save()
            messages.success(request, 'Overtime request submitted successfully.')
            return redirect('overtime_request_list')
    else:
        form = OvertimeRequestForm(initial={'hours': attendance.overtime_hours})
    
    context = {
        'form': form,
        'attendance': attendance,
    }
    return render(request, 'attendance/overtime_request_create.html', context)


# Manager Approval Views

@login_required
def manager_correction_list(request):
    if request.user.employee_profile.role not in ['MANAGER', 'HR']:
        messages.error(request, 'Access denied. Manager or HR role required.')
        return redirect('dashboard')
    
    corrections = AttendanceCorrection.objects.filter(status='PENDING').select_related('employee', 'attendance').order_by('-created_at')
    
    context = {
        'corrections': corrections,
    }
    return render(request, 'attendance/manager_correction_list.html', context)


@login_required
def manager_correction_approve(request, correction_id):
    if request.user.employee_profile.role not in ['MANAGER', 'HR']:
        messages.error(request, 'Access denied. Manager or HR role required.')
        return redirect('dashboard')
    
    correction = get_object_or_404(AttendanceCorrection, pk=correction_id, status='PENDING')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            correction.status = 'APPROVED'
            correction.manager_comment = comment
            
            # Update attendance
            if correction.requested_check_in:
                correction.attendance.check_in = correction.requested_check_in
            if correction.requested_check_out:
                correction.attendance.check_out = correction.requested_check_out
            
            # Recalculate working hours
            if correction.attendance.check_in and correction.attendance.check_out:
                duration = correction.attendance.check_out - correction.attendance.check_in
                correction.attendance.working_hours = round(duration.total_seconds() / 3600, 2)
                
                # Recalculate overtime
                if correction.attendance.shift:
                    standard_hours = correction.attendance.shift.working_hours
                    if correction.attendance.working_hours > standard_hours:
                        correction.attendance.overtime_hours = round(correction.attendance.working_hours - standard_hours, 2)
                    else:
                        correction.attendance.overtime_hours = 0
            
            correction.attendance.save()
            messages.success(request, 'Correction approved and attendance updated.')
        elif action == 'reject':
            correction.status = 'REJECTED'
            correction.manager_comment = comment
            messages.success(request, 'Correction rejected.')
        
        correction.save()
        return redirect('manager_correction_list')
    
    context = {
        'correction': correction,
    }
    return render(request, 'attendance/manager_correction_approve.html', context)


@login_required
def manager_overtime_list(request):
    if request.user.employee_profile.role not in ['MANAGER', 'HR']:
        messages.error(request, 'Access denied. Manager or HR role required.')
        return redirect('dashboard')
    
    overtime_requests = OvertimeRequest.objects.filter(status='PENDING').select_related('employee', 'attendance').order_by('-created_at')
    
    context = {
        'overtime_requests': overtime_requests,
    }
    return render(request, 'attendance/manager_overtime_list.html', context)


@login_required
def manager_overtime_approve(request, overtime_id):
    if request.user.employee_profile.role not in ['MANAGER', 'HR']:
        messages.error(request, 'Access denied. Manager or HR role required.')
        return redirect('dashboard')
    
    overtime = get_object_or_404(OvertimeRequest, pk=overtime_id, status='PENDING')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            overtime.status = 'APPROVED'
            overtime.manager_comment = comment
            messages.success(request, 'Overtime approved.')
        elif action == 'reject':
            overtime.status = 'REJECTED'
            overtime.manager_comment = comment
            messages.success(request, 'Overtime rejected.')
        
        overtime.save()
        return redirect('manager_overtime_list')
    
    context = {
        'overtime': overtime,
    }
    return render(request, 'attendance/manager_overtime_approve.html', context)


# HR Leave Management

@login_required
def hr_leave_list(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    leaves = Leave.objects.select_related('employee').all().order_by('-start_date')
    
    context = {
        'leaves': leaves,
    }
    return render(request, 'attendance/hr_leave_list.html', context)


@login_required
def hr_leave_create(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave record created successfully.')
            return redirect('hr_leave_list')
    else:
        form = LeaveForm()
    
    context = {
        'form': form,
    }
    return render(request, 'attendance/hr_leave_create.html', context)


@login_required
def hr_leave_edit(request, leave_id):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    leave = get_object_or_404(Leave, pk=leave_id)
    
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave record updated successfully.')
            return redirect('hr_leave_list')
    else:
        form = LeaveForm(instance=leave)
    
    context = {
        'form': form,
        'leave': leave,
    }
    return render(request, 'attendance/hr_leave_edit.html', context)
