from django import forms
from .models import *
from django.forms import Form, ModelForm, DateField, widgets
from django.forms import DateTimeField, DateTimeInput
from datetime import date, datetime, timedelta 


class ExpensesForm(forms.ModelForm):	
	class Meta:
		model = Expenses
		fields = ['Submitted_By','Approval_Request_To','Related_To','Sales_Order','Purpose','Remarks', 'Lock_Status']

	def clean(self): 
	    cleaned_data = self.cleaned_data
	    if not cleaned_data.get('Date'):
	    	cleaned_data['Date'] = date.today()
	    return cleaned_data 

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class ExpensesItemsForm(forms.ModelForm):	
	class Meta:
		model = Exp_Items
		exclude = ['Expenses']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })	        

class IssuedAmountsForm(forms.ModelForm):	
	class Meta:
		model = Debit_Amounts
		fields = ['Paid_To','Expenses','Issued_To','Party_Name','Related_To','Against','Amount_to_be_Pay','Issued_Amount','Issued_Date',
		'Payment_Mode','Cheque_Details','Purpose','Approved_By','Issued_By','Attach']

	def clean(self): 
	    cleaned_data = self.cleaned_data
	    if not cleaned_data.get('Issued_Date'):
	    	cleaned_data['Issued_Date'] = date.today()
	    return cleaned_data 

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })


class AttendanceForm(forms.ModelForm):
	class Meta:
		model = Attendance
		exclude = ['Total_Hours', 'Issued_By', 'Is_Manual']
		widgets = {'Date': widgets.DateInput(attrs={'type': 'date'}), 'Start_Time': widgets.TimeInput(attrs={'type': 'time'}), 'End_Time': widgets.TimeInput(attrs={'type': 'time'})}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})

class AttendanceForm1(forms.ModelForm):
	class Meta:
		model = Attendance
		exclude = ['Total_Hours', 'Issued_By', 'Is_Manual']
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})

class DeclareDayAsForm(forms.ModelForm):	
	class Meta:
		model = DeclareDayAs
		exclude = ['Lock_Status']
		widgets = {'Date': widgets.DateInput(attrs={'type': 'date'})}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})

class EmployMonthlySalaryForm(forms.ModelForm):	
	class Meta:
		model = Monthly_Salaries
		fields = ['Issued_Salary', 'LOP', 'OT_Amount', 'PF', 'ESI', 'TDS', 'Other_Deductions', 'Salary_Advance']
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})       