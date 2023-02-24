from django import forms
from .models import *
from Projects.basedata import projectname
from django.forms import Form, ModelForm, DateField, widgets
from django.forms import DateTimeField, DateTimeInput
from django.shortcuts import get_object_or_404


class OrdersForm(forms.ModelForm):	
	class Meta:
		model = Orders
		exclude = ['ds', 'RC', 'Related_Project', 'Add_Product', 'Order_No', 'Work_Status', 'Order_Type', 'Order_Reference_Person', 'Quote',
		'Payment_Status',  'Final_Status', 'Billing_Status', 'Can_Gen_Invoice', 'Is_Billed', 'FY', 'Order_No_1', 'DSP_Status', 'INST_Status']

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
		exclude = ['ds', 'RC', 'Related_Project', 'Add_Product', 'Order_No', 'Work_Status', 'Order_Type', 'Order_Reference_Person', 'Quote',
		'Payment_Status',  'Final_Status', 'Billing_Status', 'Can_Gen_Invoice', 'Is_Billed', 'FY', 'Order_No_1', 'DSP_Status', 'INST_Status']
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
		exclude = ['user', 'As_Advance_Amount', 'Order_No', 'Invoice_No', 'user', 'Payment_Type', 'Adjusted_Amount']
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
		exclude = ['user', 'As_Advance_Amount', 'Payment_Type', 'Adjusted_Amount']
		widgets = {'Payment_Date': widgets.DateInput(attrs={'type': 'datetime-local'}),'Next_Commitment_Date': widgets.DateInput(attrs={'type': 'date'})}
	
	def __str__(self):
		return str(self.Invoice_No)

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
		exclude = ['user', 'As_Advance_Amount', 'Payment_Type', 'Order_No', 'Adjusted_Amount']
		
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
		'Credit_Days', 'GST_Reverse_Charges', 'Lock_Status', 'Is_Proforma', 'Invoice_No_Format', 'Set_For_Returns', 'Payment_Terms', 'Adjusted_Amount']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })
	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Last_Update')
	    if not f1:
	        cleaned_data['Last_Update'] = date.today()
	    return cleaned_data

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
	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Last_Update')
	    if not f1:
	        cleaned_data['Last_Update'] = date.today()
	    return cleaned_data	

class ManualInvoicesForm(forms.ModelForm):
	GST_Amount	= forms.FloatField(required=True, help_text='only GST Amount')	
	class Meta:
		model = Invoices
		# exclude = ['user']
		fields = ['Invoice_No','Invoice_Date','Invoice_Amount','GST_Amount','Credit_Days', 'Adjusted_Amount', 'Attach']
		widgets = {'Invoice_Date': widgets.DateInput(attrs={'type': 'datetime-local'})}

	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Invoice_Date')
	    f2 = cleaned_data.get('Last_Update')
	    if not f1:
	        cleaned_data['Invoice_Date'] = datetime.now()
	    if not f2:
	    	cleaned_data['Last_Update'] = date.today()
	    return cleaned_data	

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class ManualInvoicesForm1(forms.ModelForm):
	GST_Amount	= forms.FloatField(required=True, help_text='only GST Amount')	
	class Meta:
		model = Invoices
		# exclude = ['user']
		fields = ['Invoice_No','Invoice_Date','Invoice_Amount','GST_Amount','Credit_Days', 'Adjusted_Amount', 'Attach']

	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Invoice_Date')
	    f2 = cleaned_data.get('Last_Update')
	    if not f1:
	        cleaned_data['Invoice_Date'] = datetime.now()
	    if not f2:
	    	cleaned_data['Last_Update'] = date.today()
	    return cleaned_data	

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
		exclude = ['user', 'Invoice_No', 'RC']

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
		widgets = {'Date': widgets.DateInput(attrs={'type': 'date'})}

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

class OrdersFormQ(forms.ModelForm):	
	class Meta:
		model = Orders
		fields = ['user', 'PO_No', 'Order_Details', 'Order_Value', 'Order_Received_Date', 'Quote', 'Attach']
		widgets = {'Order_Received_Date': widgets.DateInput(attrs={'type': 'datetime-local'})}

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

class InvoicesFormQ(forms.ModelForm):
	class Meta:
		model = Invoices
		# exclude = ['user']
		fields = ['Invoice_No','Invoice_Date','Invoice_Amount', 'Attach']
		widgets = {'Invoice_Date': widgets.DateInput(attrs={'type': 'datetime-local'})}

	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Invoice_Date')
	    f2 = cleaned_data.get('Last_Update')
	    if not f1:
	        cleaned_data['Invoice_Date'] = datetime.now()
	    if not f2:
	    	cleaned_data['Last_Update'] = date.today()
	    return cleaned_data	

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class PaymentsFormQ(forms.ModelForm):	
	class Meta:
		model = Payment_Status
		fields = ['Received_Amount', 'Payment_Date', 'Account_Name', 'Reference_No']
		widgets = {
            'Payment_Date': widgets.DateInput(attrs={'type': 'datetime-local'})
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


class ManualQuotesForm(forms.ModelForm):	
	class Meta:
		model = Manual_Quotes
		exclude = ['ds', 'RC', 'Related_Project']
		widgets = {'Date': widgets.DateInput(attrs={'type': 'datetime-local'})}

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


class DispatchesForm(forms.ModelForm):	
	class Meta:
		model = Dispatches
		exclude = ['Order', 'user', 'Installation_Status', 'Installation_Date', 'Installation_Details', 'Pending_Installation_Work', 'Transport_Mode', 'Vehicle_No', 'LRR_No', 'Vehicle_Type']
		widgets = {'Dispatch_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields: self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})

class DispatchesForm1(forms.ModelForm):	
	class Meta:
		model = Dispatches
		exclude = ['user', 'Installation_Status', 'Installation_Date', 'Installation_Details', 'Pending_Installation_Work', 'Transport_Mode', 'Vehicle_No', 'LRR_No', 'Vehicle_Type']
		widgets = {'Dispatch_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields: self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})

class InstallationsForm(forms.ModelForm):	
	class Meta:
		model = Installations
		exclude = ['Order', 'user']
		widgets = {'Installation_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields: self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})