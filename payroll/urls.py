from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_list, name='payroll_list'),
    path('hr/salary-structures/', views.hr_salary_structure_list, name='hr_salary_structure_list'),
    path('hr/salary-structures/create/', views.hr_salary_structure_create, name='hr_salary_structure_create'),
    path('hr/salary-structures/<int:structure_id>/edit/', views.hr_salary_structure_edit, name='hr_salary_structure_edit'),
    path('hr/payroll/', views.hr_payroll_list, name='hr_payroll_list'),
    path('hr/payroll/run/', views.hr_payroll_run, name='hr_payroll_run'),
    path('hr/payroll/<int:payroll_id>/approve/', views.hr_payroll_approve, name='hr_payroll_approve'),
    path('hr/payroll/<int:payroll_id>/lock/', views.hr_payroll_lock, name='hr_payroll_lock'),
]
