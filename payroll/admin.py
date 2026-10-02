from django.contrib import admin
from .models import SalaryStructure, Payroll, Notification


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['employee', 'basic_salary', 'effective_from']
    list_filter = ['effective_from']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'gross_salary', 'net_salary', 'status']
    list_filter = ['status', 'month', 'year']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
