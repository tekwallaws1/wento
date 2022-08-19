import django_filters
from django import forms
from django.db import models
from django_filters import DateFilter, NumberFilter, CharFilter, BooleanFilter
from .models import *

class ExpensesItemsFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='From_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='To_Date', lookup_expr='lte')
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
		fields = ['Employ','Issued_By','Approved_By','Payment_Mode']