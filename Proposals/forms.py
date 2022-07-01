from django import forms
from .models import *

class ProposalForm(forms.ModelForm):	
	class Meta:
		model = Proposal
		exclude = ['Date', 'Proposal_No', 'Proposal_No_1', 'Is_Gen', 'Power_Bill']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class ProposalEditForm(forms.ModelForm):	
	class Meta: 
		model = Proposal
		exclude = ['Proposal_No_1', 'Is_Gen']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class Proposal1Form(forms.ModelForm):	#For Customer
	class Meta:
		model = Proposal
		exclude = ['Date', 'Proposal_No', 'Proposal_No_1', 'Is_Gen', 'Inverter_Capacity']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class QuoteForm(forms.ModelForm):	
	class Meta:
		model = Quote
		exclude = ['Date', 'Proposal_No', 'Proposal_No_1', 'Rivision', 'Account', 'From_Company', 'Proposal_To', 'Supplier_Add_On_Cost', 'Tender_Cost', 'Type', 'GST_Amount', 'Status']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class CompanyDetailsForm(forms.ModelForm):	
	class Meta:
		model = CompanyDetails
		exclude = ['Status', 'ds']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class PowerCatForm(forms.ModelForm):	
	class Meta:
		model = PowerCat
		exclude = ['Revision_Date', 'Status', 'ds', 'Ref_No']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })

class CostingForm(forms.ModelForm):	
	class Meta:
		model = Costing
		exclude = ['Revision_Date', 'Ref_No', 'ds', 'Ref_No']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for _, value in self.fields.items():
			value.widget.attrs['placeholder'] = value.help_text
		for field in self.fields:
			self.fields[field].widget.attrs.update({
	            'class': 'form-control mb-4'
	        })