from django import forms
from .models import *
from django.forms import Form, ModelForm, DateField, widgets
from django.forms import DateTimeField, DateTimeInput

		
# Why because for datetime field if use widget class datetime-local, for edit datetime is coming empty
class PurchasesForm(forms.ModelForm):
	class Meta:
		model = Purchases
		fields = ['Order', 'PO_From', 'Vendor', 'Vendor_Contact', 'Purchase_Details', 'Shipping_To', 'PO_No', 'PO_Date', 'Payment_Term_1', 'Payment_Term_2',
		'Packing_and_Forwarding', 'Delivery_Date', 'Warranty','Warranty_In', 'Lock_Status', 'Contact']
	
		# widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'})}

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
	    f1 = cleaned_data.get('PO_Date') # this is not None if user left the <input/> empty
	    f2 = cleaned_data.get('Delivery_Date')
	    
	    if not f1:
	    	cleaned_data['PO_Date'] = datetime.now()
	    if not f2:
	    	cleaned_data['Delivery_Date'] = date.today()

	    return cleaned_data

class POForm(forms.ModelForm):	
	class Meta:
		model = Purchases
		fields = ['Final_Status']

	def clean(self): 
	    cleaned_data = self.cleaned_data
	    if not cleaned_data.get('PO_Date'):
	    	cleaned_data['PO_Date'] = datetime.now()
	    return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class ManualPurchasesForm(forms.ModelForm):
	class Meta:
		model = Purchases
		fields = ['PO_From','Vendor','Vendor_Contact','Purchase_Details','PO_No','PO_Date',
		'PO_Value','GST_Amount','Delivery_Date','Warranty','Warranty_In', 'Attach', 'Final_Status']
	
		widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'}), 'PO_Date': widgets.DateInput(attrs={'type': 'date'})}

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
	    f1 = cleaned_data.get('PO_Date') # this is not None if user left the <input/> empty
	    f2 = cleaned_data.get('Delivery_Date')
	    
	    if not f1:
	    	cleaned_data['PO_Date'] = datetime.now()
	    if not f2:
	    	cleaned_data['Delivery_Date'] = date.today()

	    return cleaned_data

class ManualPurchasesForm1(forms.ModelForm):
	class Meta:
		model = Purchases
		fields = ['PO_From','Vendor','Vendor_Contact','Purchase_Details','PO_No','PO_Date',
		'PO_Value','GST_Amount','Delivery_Date','Warranty','Warranty_In', 'Attach', 'Final_Status']
	
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
	    f1 = cleaned_data.get('PO_Date') # this is not None if user left the <input/> empty
	    f2 = cleaned_data.get('Delivery_Date')
	    
	    if not f1:
	    	cleaned_data['PO_Date'] = datetime.now()
	    if not f2:
	    	cleaned_data['Delivery_Date'] = date.today()

	    return cleaned_data

class PODeliveryForm(forms.ModelForm):
	class Meta:
		model = PO_Delivery_Status
		exclude = ['user','PO_No']
	
		widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'}), 'Next_Commitment_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class PODeliveryForm1(forms.ModelForm):
	class Meta:
		model = PO_Delivery_Status
		exclude = ['user', 'PO_No']
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })		


class POPaymentsForm(forms.ModelForm):	
	class Meta:
		model = Vendor_Payment_Status
		fields = ['Paid_Amount', 'Payment_Date', 'Next_Commitment_Date', 'PO_No']
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

class VendorPaymentForm(forms.ModelForm):	
	class Meta:
		model = Vendor_Payment_Status
		fields = ['PO_No', 'Invoice_No', 'Paid_Amount', 'Payment_Date', 'Next_Commitment_Date']
		widgets = {'Payment_Date': widgets.DateInput(attrs={'type': 'datetime-local'}),'Next_Commitment_Date': widgets.DateInput(attrs={'type': 'date'})}

	def clean(self): 
	    cleaned_data = self.cleaned_data
	    if not cleaned_data.get('Payment_Date'):
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

class VendorPaymentForm1(forms.ModelForm):	
	class Meta:
		model = Vendor_Payment_Status
		fields = ['PO_No', 'Invoice_No', 'Paid_Amount', 'Payment_Date', 'Next_Commitment_Date']
		# widgets = {'Payment_Date': widgets.DateInput(attrs={'type': 'datetime-local'}),'Next_Commitment_Date': widgets.DateInput(attrs={'type': 'date'})}

	def clean(self): 
	    cleaned_data = self.cleaned_data
	    if not cleaned_data.get('Payment_Date'):
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

class POTCForm(forms.ModelForm):
	class Meta:
		model = PO_Terms_Conditions
		exclude = ['PO_No']
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })		

class POItemsForm(forms.ModelForm):	
	class Meta:
		model = PO_Items
		exclude = ['user', 'PO_No']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class CopyPOItemsForm(forms.ModelForm):	
	class Meta:
		model = Copy_PO_Items
		exclude = ['user', 'PO_No', 'Item_From_Product']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class VendorInvoicesForm(forms.ModelForm):	
	class Meta:
		model = Vendor_Invoices
		fields = ['Against', 'PO_No', 'Vendor', 'Invoice_Description', 'Invoice_No', 'Invoice_Date', 'Invoice_Amount', 'GST_Amount', 'Credit_Days', 'Attach']
		widgets = {'Invoice_Date': widgets.DateInput(attrs={'type': 'datetime-local'})}

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

class VendorInvoicesForm1(forms.ModelForm):	
	class Meta:
		model = Vendor_Invoices
		fields = ['Against','PO_No','Vendor','Invoice_Description', 'Invoice_No', 'Invoice_Date', 'Invoice_Amount', 'GST_Amount', 'Credit_Days', 'Attach']

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

class ProductsForm(forms.ModelForm):
	class Meta:
		model = Products
		exclude = ['user', 'Stock']
		widgets = {'Active_From': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})		
	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Active_From')  	     
	    if not f1:
	    	cleaned_data['Active_From'] = date.today()
	    return cleaned_data

class ProductsForm1(forms.ModelForm):
	class Meta:
		model = Products
		exclude = ['user', 'Stock']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})		
	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Active_From')  	     
	    if not f1:
	    	cleaned_data['Active_From'] = date.today()
	    return cleaned_data

class ProductsPriceForm(forms.ModelForm):
	class Meta:
		model = Product_Price
		exclude = ['user', 'Product_Name', 'CESS', 'TDS_Deductions', 'Other_Taxes']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})		
	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('GST')    
	    if not f1:
	    	cleaned_data['GST'] = 0
	    return cleaned_data

class StockMovementForm(forms.ModelForm):
	class Meta:
		model = Product_Movement
		exclude = ['user', 'Stock']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})		
	def clean(self):
	    cleaned_data = self.cleaned_data
	    f1 = cleaned_data.get('Date') # this is not None if user left the <input/> empty	    
	    if not f1:
	    	cleaned_data['Date'] = date.today()
	    return cleaned_data

class QuotationForm(forms.ModelForm):
	class Meta:
		model = Quotes
		fields = ['Quote_To', 'Firm_Name', 'Reference_Person', 'Phone_Number', 'Email', 'Location']
	
		# widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items(): 
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class QuotationEditForm(forms.ModelForm):
	class Meta:
		model = Quotes
		fields = ['Quote_From', 'Quote_No', 'Date', 'Subject', 'Valid_Days', 'Comments', 'Thanks_Note', 
		'Lock_Status', 'Quote_To', 'Firm_Name', 'Reference_Person', 'Phone_Number', 'Email', 'Location']
	
		# widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items(): 
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })		

class QuoteTCForm(forms.ModelForm):
	class Meta:
		model = Quote_TC
		exclude = ['Quote_No']
	
		# widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items(): 
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class QuoteItemsForm(forms.ModelForm):
	class Meta:
		model = Quote_Items
		exclude = ['user', 'Quote_No']
	
		# widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items(): 
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class CopyQuoteItemsForm(forms.ModelForm):
	class Meta:
		model = Copy_Quote_Items
		exclude = ['user', 'Quote_No', 'Item_From_Product']
	
		# widgets = {'Delivery_Date': widgets.DateInput(attrs={'type': 'date'})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items(): 
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class QuoteFileForm(forms.Form):
	Attach = forms.FileField()