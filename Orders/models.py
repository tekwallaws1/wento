from django.db import models
from Projects.models import *
from Products.models import * 
from UserAccounts.models import *
from django.contrib.auth.models import User
# Create your models here.    

order_by = (('By PO', 'By PO'), ('By Mail', 'By Mail'), ('By Phone', 'By Phone'), ('By Reference', 'By Reference'))
uom = (('No','No'), ('Set', 'Set'), ('Kg', 'Kg'), ('Mtr', 'Mtr'), ('Ltr', 'Ltr'), ('Bag', 'Bag')) 

class Orders(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	RC                  = models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL)
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL) 
	Customer_Name 		= models.ForeignKey(CustDt, null=True, on_delete=models.SET_NULL)
	Order_Details   	= models.CharField(max_length=500, null=True, blank=True, help_text='overall order short description')
	Order_No 			= models.CharField(max_length=30, blank=True, null=True, unique=True, help_text='internal purpose - order reference number')
	Order_No_1			= models.IntegerField(default=0, null=True, blank=True) #backend
	FY 					= models.CharField(max_length=10, blank=True, null=True, help_text='financial year such as 22-23, 23-24 etc..')	
	Order_Value			= models.FloatField(default=0, max_length=20, null=True,  help_text='order value or estimated value')
	Order_Type 			= models.CharField(max_length=20, null=True, choices=(('Confirmed', 'Confirmed'), ('Pipeline', 'Pipeline')))
	Order_Received_Date = models.DateTimeField(blank=True, null=True, help_text='received order date')
	Order_Reference_Person	= models.ForeignKey(CustContDt, on_delete=models.SET_NULL, blank=True, null=True, help_text='order reference person name')
	Order_Through 		= models.CharField(max_length=20, choices=order_by, null=True)
	Work_Status			= models.ForeignKey('Work_Status', null=True, blank=True, on_delete=models.SET_NULL) 
	Payment_Status		= models.ForeignKey('Payment_Status', null=True, blank=True, on_delete=models.SET_NULL) 
	Billing_Status		= models.ForeignKey('Invoices', null=True, blank=True, on_delete=models.SET_NULL) 
	# Final_Work_Status	= models.BooleanField(default=False, help_text='Final Work Status')
	Final_Status		= models.BooleanField(default=False, help_text='Total Works and Payments Status')
	PO_No 				= models.CharField(max_length=30, null=True, help_text='internal received order number')
	PO_Status			= models.BooleanField(default=False, help_text='PO work completion status, mark if PO work completed')
	Can_Gen_Invoice		= models.BooleanField(default=True, help_text='False if PO amount less than all onvoices amount') #backend
	Is_Billed			= models.BooleanField(default=False) #backend
	Attach				= models.FileField(upload_to='orders/', blank=True, null=True, help_text='attach PO copy if available')
	Attach_Excels		= models.FileField(upload_to='orders/', blank=True, null=True, help_text='attach excel copy if available')
	ds					= models.BooleanField(default=True)
	Quote 				= models.ForeignKey('Manual_Quotes', null=True, blank=True, on_delete=models.SET_NULL)
	DSP_Status 			= models.CharField(max_length=30, null=True, blank=True, choices=(('Fully Dispatched', 'Fully Dispatched'), ('Partially Dispatched', 'Partially Dispatched')))
	INST_Status 		= models.CharField(max_length=30, null=True, blank=True, choices=(('Fully Installed', 'Fully Installed'), ('Partially Installed', 'Partially Installed'), ('Not Installed', 'Not Installed')))

	def save(self, *args, **kwargs): #if file updated it will delete old file and replace
	    try:
	        this = Orders.objects.get(id=self.id)
	        if this.Attach != self.Attach:
	        	this.Attach.delete(save=False)
	    except:
	    	pass  # when new file then we do nothing, normal case
	    super().save(*args, **kwargs)

	def __str__(self):
		return str(self.Customer_Name.Customer_Name)+'-'+str(self.PO_No)+'-'+str(self.Order_Value)

	# def process_request(self, request):
	# 	if request.user.username == 'praveen' or  request.user.username == '9849203852' or  request.user.username == '9010654596':
	# 		def __str__(self):
	# 			return str(self.Customer_Name.Customer_Name)+'-'+str(self.PO_No)+'-'+str(self.Order_Value)
	# 	else:
	# 		def __str__(self):
	# 			return str(self.Customer_Name.Customer_Name)+'-'+str(self.PO_No)

class Order_Items(models.Model): 
	Order_No 		    = models.ForeignKey(Orders, null=True, blank=True, on_delete=models.CASCADE)
	Add_Item   			= models.ForeignKey(Products, null=True, on_delete=models.SET_NULL)
	Quantity			= models.FloatField(default=0, max_length=10, null=True, help_text='no of items')
	
	def __str__(self):
		return str(self.Add_Item.Product_Name)+'-'+str(self.Quantity)

class Work_Status(models.Model):
	Order_No 			= models.ForeignKey(Orders, null=True, blank=True, on_delete=models.CASCADE)
	Current_Status 		= models.TextField(max_length=100, null=True, help_text='current progress/status')
	Date 				= models.DateTimeField(blank=True, null=True, help_text='status update date')
	Next_Task			= models.TextField(max_length=100, null=True, blank=True, help_text='next work/stage details want to do')
	Target_Date 		= models.DateTimeField(blank=True, null=True, help_text='schedule/target date for next work')
	Closing_Status		= models.BooleanField(default=False, help_text='tick if product delivered and excecuted')
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 

	def __str__(self):
		return str(self.Order_No)+'-'+str(self.Date)+'-'+str(self.Current_Status)

class Payment_Status(models.Model):
	Invoice_No 			= models.ForeignKey('Invoices', null=True, blank=True, on_delete=models.SET_NULL)
	Order_No 			= models.ForeignKey(Orders, null=True, blank=True, on_delete=models.SET_NULL)
	Received_Amount		= models.FloatField(default=0, max_length=20, null=True, help_text='received payment against this order')
	Payment_Type 		= models.CharField(max_length=20, null=True, blank=True, choices=(('Due', 'Due'), ('Advance', 'Advance')))
	Account_Name 		= models.ForeignKey(Bank_Accounts, null=True, on_delete=models.SET_NULL)
	Reference_No 		= models.CharField(max_length=30, null=True, blank=True, help_text='transaction no/cheque no')
	Payment_Date 		= models.DateTimeField(blank=True, null=True, help_text='payment received date')
	As_Advance_Amount	= models.FloatField(default=0, max_length=20, null=True, blank=True, help_text='If any as advance after clear all bills')
	Next_Commitment_Date= models.DateField(blank=True, null=True, help_text='specify if any next payment commitment date')
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	Adjusted_Amount		= models.FloatField(default=0, max_length=20, null=True, blank=True, help_text='adjusted due payment')

	def __str__(self):
		return str(self.Order_No)+'-'+str(self.Received_Amount)+'-'+str(self.Payment_Date)


class Invoices(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
	Order 		        = models.ForeignKey(Orders, null=True, blank=True, on_delete=models.SET_NULL)
	Billing_From 		= models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL, related_name='billing')
	Billing_To 			= models.ForeignKey(CustDt, null=True, blank=True, on_delete=models.SET_NULL, related_name='shipping')
	Shipping_To 		= models.ForeignKey(CustDt, null=True, blank=True, on_delete=models.SET_NULL)
	Bank_Details 		= models.ForeignKey(Bank_Accounts, null=True, blank=True, on_delete=models.SET_NULL)	
	Delivery_Note 		= models.ForeignKey('Delivery_Note', null=True, blank=True, on_delete=models.SET_NULL)
	Terms_and_Conditions= models.ForeignKey('Terms_Conditions', null=True, blank=True, on_delete=models.SET_NULL)		
	Invoice_No 			= models.CharField(max_length=30, blank=True, null=True, help_text='invoice/bill no')
	Invoice_No_1		= models.IntegerField(default=0, null=True, blank=True) #backend
	Invoice_No_Format 	= models.ForeignKey(No_Formats, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to=models.Q(No_Format_Related_To__in = ['Invoice', 'Proforma Invoice']))
	FY 					= models.CharField(max_length=10, blank=True, null=True, help_text='financial year such as 22-23, 23-24 etc..')
	Invoice_Date 		= models.DateTimeField(blank=True, null=True, help_text='billed date')
	Invoice_Amount		= models.FloatField(max_length=20, default=0, null=True, help_text='including all taxes')
	GST_Amount			= models.FloatField(default=0, max_length=10,  null=True, help_text='only GST Amount, leave as 0 if no GST')
	CESS_Amount			= models.FloatField(default=0, max_length=10, blank=True, null=True, help_text='CESS Amount')	
	GST_Reverse_Charges	= models.BooleanField(default=False, help_text='default nill, if applicable mark it')
	Credit_Days			= models.IntegerField(default=0, null=True,  help_text='credit in days such as 0, 15, 30, 60 etc..')
	Payment_Terms 		= models.CharField(max_length=100, blank=True, null=True,  help_text='payment terms')
	Payment_Over_Due_Days= models.IntegerField(null=True, blank=True, help_text='overdue in days such as 0, 30 etc..')
	Payment_Due_Date 	= models.DateField(blank=True, null=True, help_text='payment due date')
	Payment_Status		= models.ForeignKey('Payment_Status', null=True, blank=True, on_delete=models.SET_NULL)
	Due_Amount			= models.FloatField(max_length=20, null=True, blank=True, help_text='Due amount till date against billed')
	Final_Payment_Status= models.BooleanField(default=False, help_text='Final Payment Status')
	Payment_Cleared_Date= models.DateTimeField(blank=True, null=True, help_text='date of payment clearing')
	Remarks 			= models.TextField(max_length=500, null=True, blank=True)
	Attach				= models.FileField(upload_to='bills/', blank=True, null=True, help_text='attach order copy if available')
	Lock_Status			= models.BooleanField(default=False, help_text='mark if wnat to lock invoice to avoid editing')
	Is_Proforma			= models.BooleanField(default=False, help_text='tick if it is proforma invoice')
	Attach				= models.FileField(upload_to='customerinvoices/', blank=True, null=True, help_text='attach invoice copy if available')	
	Is_Manual			= models.BooleanField(default=False, help_text='wether it is manual entry or online generation')
	Set_For_Returns		= models.BooleanField(default=True)
	Amended_GST_Returns_Date = models.DateField(blank=True, null=True, help_text='any date in a month which you want make returns')
	ds					= models.BooleanField(default=True)
	Last_Update 		= models.DateField(blank=True, null=True)
	Roundoff 			= models.FloatField(default=0, max_length=5, blank=True, null=True)
	Adjusted_Amount		= models.FloatField(default=0, max_length=20, null=True, blank=True, help_text='adjusted due payment')

	def save(self, *args, **kwargs): #if file updated it will delete old file and replace
	    try:
	        this = Invoices.objects.get(id=self.id)
	        if this.Attach != self.Attach:
	        	this.Attach.delete(save=False)
	    except:
	    	pass  # when new file then we do nothing, normal case
	    super().save(*args, **kwargs)

	def __str__(self):
		return str(self.Billing_To.Customer_Name)+'-'+str(self.Invoice_No)+'-'+str(self.Invoice_Amount)

class Billed_Items(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	Invoice_No 		    = models.ForeignKey(Invoices, null=True, blank=True, on_delete=models.CASCADE)
	Add_Item   			= models.ForeignKey(Product_Price, null=True, on_delete=models.SET_NULL)
	Quantity			= models.FloatField(default=0, max_length=10, null=True)
	
	def __str__(self):
		return str(self.Add_Item.Product_Name)+'-'+str(self.Quantity)

class Copy_Billed_Items(models.Model):
	Invoice_No 		    = models.ForeignKey(Invoices, null=True, blank=True, on_delete=models.CASCADE)
	Item_From_Product   = models.ForeignKey(Billed_Items, null=True, blank=True, on_delete=models.SET_NULL)
	Item_Description 	= models.TextField(max_length=1000, null=True, blank=True, help_text='Item description')
	Item_Code 			= models.CharField(max_length=15, null=True, blank=True, help_text='Item Code')
	HSN_Code			= models.IntegerField(blank=True, null=True, help_text='HSN/SAC Code for this product')
	Quantity			= models.FloatField(default=0, max_length=10, null=True, help_text='quantity')
	UOM 				= models.CharField(max_length=15, null=True, choices=uom)
	Unit_Price			= models.FloatField(default=0, max_length=15, blank=True, null=True, help_text='each unit price excluding all taxes')
	GST					= models.FloatField(default=0, max_length=5, blank=True, null=True, help_text='GST in % such as 12, 18 etc')
	CESS				= models.FloatField(default=0, max_length=5, blank=True, null=True, help_text='CESS in % if applicable')
	Other_Taxes			= models.FloatField(default=0, max_length=5, blank=True, null=True, help_text='specify if any other taxes in % only')
	
	def __str__(self):
		return str(self.Invoice_No)+'-'+str(self.Item_Description)

class Delivery_Note(models.Model): 
	Invoice_No 		    = models.ForeignKey(Invoices, null=True, blank=True, on_delete=models.CASCADE)
	Date 				= models.DateField(blank=True, null=True, help_text='date of dispatch')
	Transport_Mode   	= models.CharField(max_length=20, null=True, blank=True, choices=(('By Road', 'By Road'), ('By Air', 'By Air')))
	LUT_No   			= models.CharField(max_length=30, null=True, blank=True, help_text='lut no')
	Vehicle_No   		= models.CharField(max_length=20, null=True, blank=True, help_text='vehicle number')
	Vehicle_Type   		= models.CharField(max_length=20, null=True, blank=True, help_text='truck, bus, train, car etc..')
	Place_Of_Supply   	= models.CharField(max_length=30, null=True, blank=True, help_text='place of supply')
	LRR_No   			= models.CharField(max_length=20, null=True, blank=True, help_text='specify if any')

	def __str__(self):
		return str(self.Invoice_No)+'-'+str(self.Transport_Mode)

class Terms_Conditions(models.Model): #for particular invoice
	Invoice_No	    	 = models.ForeignKey(Invoices, null=True, blank=True, on_delete=models.CASCADE)
	Terms_and_Condition1 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition2 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition3 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition4 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	# Additional_Note 	 = models.TextField(max_length=140, null=True, blank=True, help_text='If want to put any additional note you can put here')

	def __str__(self):
		return str(self.Invoice_No)+'-'+str(self.Terms_and_Condition1)

class Sales_TC(models.Model): #By default
	RC                   = models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL)
	Terms_and_Condition1 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition2 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition3 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition4 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')

	def __str__(self):
		return str(self.Terms_and_Condition1)

class Inv_Adjust_Table(models.Model):
	Invoice_No	    	 = models.ForeignKey(Invoices, null=True, blank=True, on_delete=models.CASCADE)
	Table_No             = models.IntegerField(null=True, blank=True)
	Row_No             	 = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return str(self.Invoice_No)+'-'+str(self.Table_No)


class Manual_Quotes(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	RC                  = models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL)
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL) 
	Customer_Name   	= models.CharField(max_length=50, null=True, help_text='customer/company name')
	Phone_Number 		= models.CharField(max_length=20, null=True, help_text='Phone Number')
	Email 				= models.EmailField(max_length=50, null=True, blank=True, help_text='Email')
	Quote_Short_Description   	= models.CharField(max_length=500, null=True, blank=True, help_text='overall order short description')
	Quote_No 			= models.CharField(max_length=30, blank=True, null=True, help_text='internal purpose - quote reference number')
	Quote_Value			= models.FloatField(default=0, max_length=20, null=True, help_text='order value or estimated value')
	Date 				= models.DateTimeField(blank=True, null=True, help_text='received order date')
	Attach				= models.FileField(upload_to='manualquotes/', blank=True, null=True, help_text='attach quote copy if available')
	ds					= models.BooleanField(default=True)
	Convert_As_Order	= models.BooleanField(default=False)

	def save(self, *args, **kwargs): #if file updated it will delete old file and replace
	    try:
	        this = Manual_Quote.objects.get(id=self.id)
	        if this.Attach != self.Attach:
	        	this.Attach.delete(save=False)
	    except:
	    	pass  # when new file then we do nothing, normal case
	    super().save(*args, **kwargs)

	def __str__(self):
		return str(self.Customer_Name)+'-'+str(self.Quote_No)+'-'+str(self.Quote_Value)



class Dispatches(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	Order 		    	= models.ForeignKey(Orders, null=True, on_delete=models.CASCADE)
	Dispatch_Date 		= models.DateField(null=True, help_text='date of dispatch')
	Dispatch_Status   	= models.CharField(max_length=30, null=True, choices=(('Fully Dispatched', 'Fully Dispatched'), ('Partially Dispatched', 'Partially Dispatched')))
	Dispatch_Details   	= models.TextField(max_length=1000, null=True, blank=True, help_text='dispatch details like which material dispatced etc')
	Pending_Dispatches  = models.TextField(max_length=1000, null=True, blank=True, help_text='optional - specify if any pending material to dispatch')
	Transport_Mode   	= models.CharField(max_length=20, null=True, blank=True, choices=(('By Road', 'By Road'), ('By Air', 'By Air')))
	Vehicle_No   		= models.CharField(max_length=20, null=True, blank=True, help_text='vehicle number')
	Vehicle_Type   		= models.CharField(max_length=20, null=True, blank=True, help_text='truck, bus, train, car etc..')
	Place_Of_Supply   	= models.CharField(max_length=30, null=True, blank=True, help_text='place of supply')
	LRR_No   			= models.CharField(max_length=20, null=True, blank=True, help_text='specify if any')
	Attach				= models.FileField(upload_to='dispatches/', blank=True, null=True, help_text='attach dc or related doc if available')	

	def __str__(self):
		return str(self.Order)+'-'+str(self.Transport_Mode)


class Installations(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	Order 		    	= models.ForeignKey(Orders, null=True, blank=True, on_delete=models.CASCADE)
	Installation_Date 	= models.DateField(null=True, help_text='date of installation')
	Installation_Status = models.CharField(max_length=30, null=True, choices=(('Fully Installed', 'Fully Installed'), ('Partially Installed', 'Partially Installed')))
	Installation_Details= models.TextField(max_length=1000, null=True, blank=True, help_text='installation details like which products installed etc..')
	Pending_Installation_Work  = models.TextField(max_length=1000, null=True, blank=True, help_text='optional - specify if any pending installation')

	def __str__(self):
		return str(self.Order)+'-'+str(self.Installation_Date)