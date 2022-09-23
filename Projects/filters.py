import django_filters
from django import forms
from django.db import models
from django_filters import DateFilter, CharFilter

from .models import *

class CustomerFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	# from_date 	= DateFilter(field_name='Date', lookup_expr='gte')
	# to_date 	= DateFilter(field_name='Date', lookup_expr='lte')	
	class Meta:
		model 	= CustDt
		fields = ['Related_Project']

class VendorFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			for field in self.form.fields:
				self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	# from_date 	= DateFilter(field_name='Date', lookup_expr='gte')
	# to_date 	= DateFilter(field_name='Date', lookup_expr='lte')	
	class Meta:
		model 	= CustDt
		fields = ['Related_Project']

class CustomerLedgerFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			for field in self.form.fields:
				self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Date', lookup_expr='lte')
	customer 	= CharFilter(field_name='Partner', lookup_expr='icontains')	
	class Meta:
		model 	= Customer_Ledger
		fields = ['Date'] 