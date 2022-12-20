import django_filters
from django import forms
from django.db import models
from django_filters import DateFilter, NumberFilter, CharFilter, BooleanFilter, ModelChoiceFilter
from .models import *

class AttendanceFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	# order 	= CharFilter(field_name='Sales_Order__Related_Project__Short_Name', lookup_expr='icontains', label='Services')
	Sales_Order = django_filters.ModelChoiceFilter(
    queryset=Orders.objects.filter(Related_Project__Short_Name='Edu').distinct()
)

	class Meta:
		model 	= Attendance
		fields = ['Sales_Order','Day_Status']

class ExpensesItemsFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs): 
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Expenses__From_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Expenses__From_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Expenses__Total_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Expenses__Total_Amount', lookup_expr='lte')

	class Meta:
		model 	= Exp_Items
		fields = ['Expenses__Submitted_By','Expenses__Related_To','Expenses__Sales_Order','Expenses__Issued_By',
		'Expenses__Clearing_Status','Expenses__Approval_Status','Expenses__Approval_Request_To','Category']

class DebitFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Issued_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Issued_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Issued_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Issued_Amount', lookup_expr='lte')

	class Meta:
		model 	= Debit_Amounts
		fields = ['Employ','Issued_By','Approved_By','Account_Name']