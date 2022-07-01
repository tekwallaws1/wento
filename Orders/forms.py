from django import forms
from .models import *
from Projects.basedata import projectname
from django.forms import Form, ModelForm, DateField, widgets
from django.forms import DateTimeField, DateTimeInput

class OrdersForm(forms.ModelForm):	
	class Meta:
		model = Orders
		exclude = ['ds', 'user', 'Related_Project', 'Add_Product', 'Order_No', 'Work_Status', 
		'Payment_Status',  'Final_Status', 'Billing_Status', 'Can_Gen_Invoice', 'Is_Billed', 'FY', 'Order_No_1']

	def clean(self): 
	    cleaned_data = self.cleaned_data
	    if not cleaned_data.get('Order_Received_Date'):
	    	cleaned_data['Order_Received_Date'] = datetime.now()
	    if not cleaned_data.get('Credit_Days'):
	    	cleaned_data['Credit_Days'] = 0
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class OrdersEmptyForm(forms.ModelForm):	
	class Meta:
		model = Orders
		exclude = ['ds', 'user', 'Related_Project', 'Add_Product', 'Order_No', 'Work_Status', 
		'Payment_Status',  'Final_Status', 'Billing_Status', 'Can_Gen_Invoice', 'Is_Billed', 'FY', 'Order_No_1']
		widgets = {
            'Order_Received_Date': widgets.DateInput(attrs={'type': 'datetime-local'})
        }
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class OrdersPaymentsForm(forms.ModelForm):	
	class Meta:
		model = Payment_Status
		exclude = ['user', 'As_Advance_Amount', 'Order_No', 'Invoice_No', 'user', 'Payment_Type']
		widgets = {
            'Payment_Date': widgets.DateInput(attrs={'type': 'datetime-local'}),
            'Next_Commitment_Date': widgets.DateInput(attrs={'type': 'date'})
        }

	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Payment_Date') # this is not None if user left the <input/> empty
	    if not f1:
	        cleaned_data['Payment_Date'] = datetime.now()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

# Why because for datetime field if use widget class datetime-local, for edit datetime is coming empty
class PaymentsEmptyForm(forms.ModelForm):
	class Meta:
		model = Payment_Status
		exclude = ['user', 'As_Advance_Amount', 'Payment_Type']
		widgets = {'Payment_Date': widgets.DateInput(attrs={'type': 'datetime-local'}),'Next_Commitment_Date': widgets.DateInput(attrs={'type': 'date'})}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })		

class PaymentsForm(forms.ModelForm):
	class Meta:
		model = Payment_Status
		exclude = ['user', 'As_Advance_Amount', 'Payment_Type']
		
		def __init__(self, *args, **kwargs):
			self.fields['Payment_Date'].widget.attrs.update(
	            {'type':'datetime-local'},
	        )

	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Payment_Date') # this is not None if user left the <input/> empty
	    if not f1:
	        cleaned_data['Payment_Date'] = datetime.now()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class OrdersWorkForm(forms.ModelForm):	
	class Meta:
		model = Work_Status
		exclude = ['Order_No', 'user']
		widgets = {
            'Date': widgets.DateInput(attrs={'type': 'datetime-local'}), 'Target_Date': widgets.DateInput(attrs={'type': 'date'})
        }

	def clean(self):
	    cleaned_data = self.cleaned_data
	    if not cleaned_data.get('Date'):
	        cleaned_data['Date'] = datetime.now()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class WorkForm(forms.ModelForm):	
	class Meta:
		model = Work_Status
		exclude = ['user']

	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Date') # this is not None if user left the <input/> empty
	    if not f1:
	        cleaned_data['Date'] = datetime.now()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class WorkEmptyForm(forms.ModelForm):	
	class Meta:
		model = Work_Status
		exclude = ['user']
		widgets = {
            'Date': widgets.DateInput(attrs={'type': 'datetime-local'}), 'Target_Date': widgets.DateInput(attrs={'type': 'date'})
        }

	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Date') # this is not None if user left the <input/> empty
	    if not f1:
	        cleaned_data['Date'] = datetime.now()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class InvoicesForm(forms.ModelForm):	
	class Meta:
		model = Invoices
		# exclude = ['user']
		fields = ['Billing_From', 'Billing_To', 'Shipping_To', 'Bank_Details', 'Invoice_No', 'Invoice_Date', 
		'Credit_Days', 'GST_Reverse_Charges', 'Lock_Status', 'Is_Proforma', 'Invoice_No_Format']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class InvoicesForm1(forms.ModelForm):	
	class Meta:
		model = Invoices
		fields = ['Order']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class BilledItemsForm(forms.ModelForm):	
	class Meta:
		model = Billed_Items
		exclude = ['user', 'Invoice_No']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class CopyBilledItemsForm(forms.ModelForm):	
	class Meta:
		model = Copy_Billed_Items
		exclude = ['user', 'Invoice_No', 'Item_From_Product']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class DeliveryNoteForm(forms.ModelForm):	
	class Meta:
		model = Delivery_Note
		exclude = ['Invoice_No']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class InvoiceTCForm(forms.ModelForm):	
	class Meta:
		model = Terms_Conditions
		exclude = ['Invoice_No']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })