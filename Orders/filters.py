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


	user = django_filters.ModelChoiceFilter(queryset=Account.objects.filter(Status=True, ds=1, Is_Marketing_Excecutive=1))
	# billstatus = BooleanFilter(field_name='Billing_Status', lookup_expr=bill_status)
	# billstatus 	= BooleanFilter(field_name='Billing_Status', method='bill_status')

	class Meta:
		model 	= Orders
		fields = ['Customer_Name', 
		'Payment_Status__user', 'Work_Status__user', 'Is_Billed', 'Final_Status', 'PO_No', 'INST_Status', 'DSP_Status']


class PaymentsFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Payment_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Payment_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='lte')
	user = django_filters.ModelChoiceFilter(queryset=Account.objects.filter(Status=True, ds=1, Is_Marketing_Excecutive=1))

	class Meta:
		model 	= Payment_Status
		fields = ['Order_No', 'Order_No__Customer_Name', 'Account_Name']

class PaymentsFilter1(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Payment_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Payment_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Received_Amount', lookup_expr='lte')
	user = django_filters.ModelChoiceFilter(queryset=Account.objects.filter(Status=True, ds=1, Is_Marketing_Excecutive=1))

	class Meta:
		model 	= Payment_Status
		fields = ['Order_No__Customer_Name', 'Account_Name']


class WorksFilter(django_filters.FilterSet):
	from_date 	= DateFilter(field_name='Order_Received_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Order_Received_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Order_Value', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Order_Value', lookup_expr='lte')
	user = django_filters.ModelChoiceFilter(queryset=Account.objects.filter(Status=True, ds=1, Is_Marketing_Excecutive=1))

	class Meta:
		model 	= Orders
		fields = ['Customer_Name', 
		'Payment_Status__user', 'Work_Status__user', 'Is_Billed', 'Final_Status', 'PO_No']

	# class Meta:
	# 	model 	= Orders
	# 	fields = ['Work_Status__Order_No', 'Customer_Name']

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
	user = django_filters.ModelChoiceFilter(queryset=Account.objects.filter(Status=True, ds=1, Is_Marketing_Excecutive=1))

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

class ManualQuotesFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	# order 	= CharFilter(field_name='Sales_Order__Related_Project__Short_Name', lookup_expr='icontains', label='Services')
	
	from_date 	= DateFilter(field_name='Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Date', lookup_expr='lte')
	user = django_filters.ModelChoiceFilter(queryset=Account.objects.filter(Status=True, ds=1, Is_Marketing_Excecutive=1))

	class Meta:
		model 	= Manual_Quotes
		fields = ['Convert_As_Order']
