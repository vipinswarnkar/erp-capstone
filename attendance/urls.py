from django.urls import path
from . import views

urlpatterns = [
    path('today/', views.attendance_today, name='attendance_today'),
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('history/', views.attendance_history, name='attendance_history'),
    path('corrections/', views.correction_request_list, name='correction_request_list'),
    path('corrections/<int:attendance_id>/create/', views.correction_request_create, name='correction_request_create'),
    path('overtime/', views.overtime_request_list, name='overtime_request_list'),
    path('overtime/<int:attendance_id>/create/', views.overtime_request_create, name='overtime_request_create'),
    path('hr/shifts/', views.hr_shift_list, name='hr_shift_list'),
    path('hr/shifts/create/', views.hr_shift_create, name='hr_shift_create'),
    path('hr/shifts/<int:shift_id>/edit/', views.hr_shift_edit, name='hr_shift_edit'),
    path('hr/shift-assignments/', views.hr_shift_assignment_list, name='hr_shift_assignment_list'),
    path('hr/shift-assignments/create/', views.hr_shift_assignment_create, name='hr_shift_assignment_create'),
    path('hr/attendance/', views.hr_attendance_list, name='hr_attendance_list'),
    path('hr/attendance/<int:attendance_id>/finalize/', views.hr_attendance_finalize, name='hr_attendance_finalize'),
    path('hr/leaves/', views.hr_leave_list, name='hr_leave_list'),
    path('hr/leaves/create/', views.hr_leave_create, name='hr_leave_create'),
    path('hr/leaves/<int:leave_id>/edit/', views.hr_leave_edit, name='hr_leave_edit'),
    path('manager/corrections/', views.manager_correction_list, name='manager_correction_list'),
    path('manager/corrections/<int:correction_id>/approve/', views.manager_correction_approve, name='manager_correction_approve'),
    path('manager/overtime/', views.manager_overtime_list, name='manager_overtime_list'),
    path('manager/overtime/<int:overtime_id>/approve/', views.manager_overtime_approve, name='manager_overtime_approve'),
]
