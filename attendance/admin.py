from django.contrib import admin
from .models import Shift, EmployeeShift, Attendance, AttendanceCorrection, OvertimeRequest, Leave


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'working_hours', 'is_active']
    list_filter = ['is_active']


@admin.register(EmployeeShift)
class EmployeeShiftAdmin(admin.ModelAdmin):
    list_display = ['employee', 'shift', 'effective_from', 'effective_to']
    list_filter = ['shift', 'effective_from']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status', 'working_hours', 'is_finalized']
    list_filter = ['status', 'date', 'is_finalized']
    date_hierarchy = 'date'


@admin.register(AttendanceCorrection)
class AttendanceCorrectionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'attendance', 'status', 'created_at']
    list_filter = ['status', 'created_at']


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'attendance', 'hours', 'status', 'created_at']
    list_filter = ['status', 'created_at']


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status', 'start_date']
