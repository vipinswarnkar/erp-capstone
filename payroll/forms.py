from django import forms
from .models import SalaryStructure, Payroll
from accounts.models import EmployeeProfile


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = ['employee', 'basic_salary', 'hra', 'transport_allowance', 'other_allowance', 
                  'pf_percentage', 'tax_percentage', 'effective_from']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'hra': forms.NumberInput(attrs={'class': 'form-control'}),
            'transport_allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'pf_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'effective_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = EmployeeProfile.objects.filter(is_active=True)


class PayrollRunForm(forms.Form):
    MONTH_CHOICES = [(i, i) for i in range(1, 13)]
    YEAR_CHOICES = [(i, i) for i in range(2024, 2030)]
    
    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
