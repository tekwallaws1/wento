import django_filters
from django import forms
from django.db import models
from django_filters import DateFilter, NumberFilter, CharFilter, BooleanFilter

from .models import *

class PurchasesFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='PO_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='PO_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='PO_Value', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='PO_Value', lookup_expr='lte')

	class Meta:
		model 	= Purchases
		fields = ['user', 'Vendor', 'Delivery_Status', 'Final_Status']

class VendorInvoicesFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			for field in self.form.fields:
				self.form.fields[field].widget.attrs.update({'class': 'form-control'})

	from_date 	= DateFilter(field_name='Invoice_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Invoice_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Invoice_Amount', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Invoice_Amount', lookup_expr='lte')
	duestatus 	= NumberFilter(field_name='Due_Amount', lookup_expr='gte')
	clearstatus = NumberFilter(field_name='Due_Amount', lookup_expr='lte')

	class Meta:
		model 	= Vendor_Invoices
		fields = ['user', 'PO_No', 'PO_No__Vendor']     


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