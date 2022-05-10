import django_filters
from django import forms
from django.db import models
from django_filters import DateFilter, NumberFilter

from .models import *


class OrdersFilter(django_filters.FilterSet):
	def __init__(self, *args, **kwargs):
  		super().__init__(*args, **kwargs)
  		for field in self.form.fields:
  			self.form.fields[field].widget.attrs.update({'class': 'form-control'})
	from_date 	= DateFilter(field_name='Order_Received_Date', lookup_expr='gte')
	to_date 	= DateFilter(field_name='Order_Received_Date', lookup_expr='lte')
	from_value 	= NumberFilter(field_name='Order_Value', lookup_expr='gte')
	to_value 	= NumberFilter(field_name='Order_Value', lookup_expr='lte')

	class Meta:
		model 	= Orders
		fields = ['Related_Project__Project_Name', 'Customer_Name__Customer_Name', 
		'Add_Product__Product_Description', 'Status']

   