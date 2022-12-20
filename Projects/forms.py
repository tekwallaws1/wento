from django import forms
from .models import *
from django.forms import Form, ModelForm, DateField, widgets
from django.forms.widgets import CheckboxSelectMultiple

class CustomerForm(forms.ModelForm):	
	class Meta:
		model = CustDt
		exclude = ['ds', 'RC', 'State_Code', 'Related_Project']
		widgets = {
            'Active_From': widgets.DateInput(attrs={'type': 'date'})
        }

	def clean(self):
	    cleaned_data = self.cleaned_data
	    activefrom = cleaned_data.get('Active_From') # this is not None if user left the <input/> empty
	    if not activefrom:
	        cleaned_data['Active_From'] = date.today()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class CustomerContactForm(forms.ModelForm):	
	class Meta:
		model = CustContDt
		exclude = ['ds', 'Customer_Name']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class VendorForm(forms.ModelForm):	
	class Meta:
		model = VendDt
		exclude = ['ds', 'RC', 'State_Code', 'Related_Project']
		widgets = {
            'Active_From': widgets.DateInput(attrs={'type': 'date'})
        }

	def clean(self):
	    cleaned_data = self.cleaned_data
	    activefrom = cleaned_data.get('Active_From') # this is not None if user left the <input/> empty
	    if not activefrom:
	        cleaned_data['Active_From'] = date.today()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class VendorContactForm(forms.ModelForm):	
	class Meta:
		model = VendContDt
		exclude = ['ds', 'Supplier_Name']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })


class CompanyForm(forms.ModelForm):	
	class Meta:
		model = CompanyDetails
		exclude = ['ds', 'RC', 'State_Code']
		widgets = {'Active_From': widgets.DateInput(attrs={'type': 'date'})}

	def clean(self):
	    cleaned_data = self.cleaned_data
	    activefrom = cleaned_data.get('Active_From') # this is not None if user left the <input/> empty
	    if not activefrom:
	        cleaned_data['Active_From'] = date.today()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })


class CustomerFormQ(forms.ModelForm):	
	class Meta:
		model = CustDt
		fields = ['Customer_Name', 'Address_Line_1', 'Address_Line_2', 'State', 'Phone_Number_1']

	def clean(self):
	    cleaned_data = self.cleaned_data
	    activefrom = cleaned_data.get('Active_From') # this is not None if user left the <input/> empty
	    if not activefrom:
	        cleaned_data['Active_From'] = date.today()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })