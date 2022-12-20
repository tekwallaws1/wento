import django_filters
from django import forms
from django.db import models
from django_filters import DateFilter, NumberFilter, CharFilter, BooleanFilter

from .models import *

# def bill_status(self, queryset, name, value):
#         # construct the full lookup expression.
# 		lookup = '__'.join([name, 'isnull'])
# 		return queryset.filter(**{lookup: False})

class OrdersFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Order_Received_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Order_Received_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Order_Value', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Order_Value', lookup_expr='lte')
	# billstatus = BooleanFilter(field_name='Billing_Status', lookup_expr=bill_status)
	# billstatus 	= BooleanFilter(field_name='Billing_Status', method='bill_status')

	class Meta:
		model 	= Orders
		fields = ['user', 'Customer_Name', 
		'Payment_Status__user', 'Work_Status__user', 'Is_Billed', 'Final_Status', 'PO_No']


class PaymentsFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Payment_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Payment_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='lte')

	class Meta:
		model 	= Payment_Status
		fields = ['user', 'Order_No', 'Order_No__Customer_Name', 'Account_Name']

class PaymentsFilter1(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Payment_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Payment_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='lte')

	class Meta:
		model 	= Payment_Status
		fields = ['user', 'Order_No__Customer_Name', 'Account_Name']


class WorksFilter(django_filters.FilterSet):
	# def __init__(self, *args, **kwargs):
 #  		super().__init__(*args, **kwargs)
 #  		for field in self.form.fields:
 #  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	# from_date 	= DateFilter(field_name='Work_Status__Date', lookup_expr='gte')
	# to_date 	= DateFilter(field_name='Work_Status__Date', lookup_expr='lte')
	
	class Meta:
		model 	= Orders
		fields = ['Work_Status__Order_No', 'Customer_Name']

class InvoicesFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			for field in self.form.fields:
				self.form.fields[field].widget.attrs.update({'class': 'form-control'})

	from_date 	= DateFilter(field_name='Invoice_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Invoice_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Invoice_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Invoice_Amount', lookup_expr='lte')
	duestatus 	= NumberFilter(field_name='Due_Amount', lookup_expr='gte')
	clearstatus 	= NumberFilter(field_name='Due_Amount', lookup_expr='lte')

	class Meta:
		model 	= Invoices
		fields = ['Order', 'Invoice_No', 'Billing_To', 'Due_Amount']     

class VendorPaymentsFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Payment_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Payment_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Paid_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Paid_Amount', lookup_expr='lte')

	class Meta:
		model 	= Vendor_Payment_Status
		fields = ['user']