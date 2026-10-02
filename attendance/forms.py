from django import forms
from .models import AttendanceCorrection, OvertimeRequest, Leave, Shift, EmployeeShift
from accounts.models import EmployeeProfile


class AttendanceCorrectionForm(forms.ModelForm):
    class Meta:
        model = AttendanceCorrection
        fields = ['requested_check_in', 'requested_check_out', 'reason']
        widgets = {
            'requested_check_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'requested_check_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OvertimeRequestForm(forms.ModelForm):
    class Meta:
        model = OvertimeRequest
        fields = ['hours', 'reason']
        widgets = {
            'hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['employee', 'start_date', 'end_date', 'leave_type', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'start_time', 'end_time', 'grace_period_minutes', 'working_hours', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'grace_period_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'working_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeShiftForm(forms.ModelForm):
    class Meta:
        model = EmployeeShift
        fields = ['employee', 'shift', 'effective_from', 'effective_to']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'effective_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'effective_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
