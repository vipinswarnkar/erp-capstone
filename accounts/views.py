from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, EmployeeCreationForm
from .models import EmployeeProfile


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    try:
        user_profile = request.user.employee_profile
    except EmployeeProfile.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR.')
        logout(request)
        return redirect('login')
    
    context = {
        'user_profile': user_profile,
    }
    
    if user_profile.role == 'EMPLOYEE':
        return render(request, 'accounts/employee_dashboard.html', context)
    elif user_profile.role == 'MANAGER':
        return render(request, 'accounts/manager_dashboard.html', context)
    elif user_profile.role == 'HR':
        return render(request, 'accounts/hr_dashboard.html', context)
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def hr_employee_list(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    employees = EmployeeProfile.objects.all().order_by('-created_at')
    context = {
        'employees': employees,
    }
    return render(request, 'accounts/hr_employee_list.html', context)


@login_required
def hr_employee_create(request):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee created successfully.')
            return redirect('hr_employee_list')
    else:
        form = EmployeeCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/hr_employee_create.html', context)


@login_required
def hr_employee_edit(request, employee_id):
    if request.user.employee_profile.role != 'HR':
        messages.error(request, 'Access denied. HR role required.')
        return redirect('dashboard')
    
    employee = get_object_or_404(EmployeeProfile, pk=employee_id)
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully.')
            return redirect('hr_employee_list')
    else:
        form = EmployeeCreationForm(instance=employee)
    
    context = {
        'form': form,
        'employee': employee,
    }
    return render(request, 'accounts/hr_employee_edit.html', context)
