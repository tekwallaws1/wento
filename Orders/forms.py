from django import forms
from .models import *

# class CustomerDetailsForm(forms.ModelForm):	
# 	class Meta:
# 		model = CustomerDetails
# 		fields = '__all__'

# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })

# class ContactDetailsForm(forms.ModelForm):	
# 	class Meta:
# 		model = ContactDetails
# 		fields = '__all__'

# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })

# class VendorDetailsForm(forms.ModelForm):	
# 	class Meta:
# 		model = VendorDetails
# 		fields = '__all__'

# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })

# class OrdersForm(forms.ModelForm):
# 	class Meta:
# 		model = Orders
# 		fields = '__all__'
		
# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })


# class PurchaseForm(forms.ModelForm):
# 	class Meta:
# 		model = Purchase
# 		fields = '__all__'

# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })


# class BillingDetailsForm(forms.ModelForm):
# 	class Meta:
# 		model = BillingDetails
# 		fields = '__all__'
# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })

# class PaymentDetailsForm(forms.ModelForm):
# 	class Meta:
# 		model = PaymentDetails
# 		fields = '__all__'

# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })

# class WorkProgressForm(forms.ModelForm):
# 	class Meta:
# 		model = WorkProgress
# 		fields = '__all__'

# class ExpensesForm(forms.ModelForm):
# 	class Meta:
# 		model = Expenses
# 		fields = '__all__'

# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		for _, value in self.fields.items():
# 			value.widget.attrs['placeholder'] = value.help_text
# 		for field in self.fields:
# 			self.fields[field].widget.attrs.update({
# 	            'class': 'form-control mb-4'
# 	        })