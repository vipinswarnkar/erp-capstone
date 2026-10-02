from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('hr/employees/', views.hr_employee_list, name='hr_employee_list'),
    path('hr/employees/create/', views.hr_employee_create, name='hr_employee_create'),
    path('hr/employees/<int:employee_id>/edit/', views.hr_employee_edit, name='hr_employee_edit'),
]
