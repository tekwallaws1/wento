from django.db import models
from Projects.models import *
from Orders.models import * 
from UserAccounts.models import *
# Create your models here.  

uom = (('No','No'), ('Set', 'Set'), ('Kg', 'Kg'), ('Mtr', 'Mtr'), ('Ltr', 'Ltr'), ('Bag', 'Bag'))

class Products(models.Model):
	Product_Name 		= models.TextField(max_length=1000, null=True, unique=True, help_text='product name')
	Product_Type		= models.CharField(max_length=30, null=True, blank=True, choices=(('Finished Goods', 'Finished Goods'), ('Services', 'Services'), ('Raw Material', 'Raw Material')))
	Make 		 		= models.CharField(max_length=50, null=True, blank=True, help_text='product make')
	Model_No 			= models.CharField(max_length=30, null=True, blank=True, help_text='Model No/Part No/Ref No')
	Serial_No 			= models.CharField(max_length=30, null=True, unique=True, blank=True, help_text='product serial number if available')
	BOM_No 				= models.CharField(max_length=15, null=True, unique=True, blank=True, help_text='BOM No for your internal reference')
	UOM 				= models.CharField(max_length=15, null=True, choices=uom)
	Date 				= models.DateTimeField(blank=True, null=True, help_text='product added/updated date')
	Stock				= models.FloatField(max_length=10, null=True, blank=True, help_text='Present Stock')	
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL, help_text='leave empty if product meant for many projects') 	
	Attach				= models.FileField(upload_to='productdatasheets/', blank=True, null=True, help_text='attach product datasheet if available')
	Status				= models.BooleanField(default=True, help_text='product active status')
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 

	def __str__(self):
		return str(self.Product_Name)+'-'+str(self.UOM)

	def save(self, *args, **kwargs): #if file updated it will delete old file and replace
	    try:
	        this = Products.objects.get(id=self.id)
	        if this.Attach_Doc != self.Attach_Doc:
	        	this.Attach_Doc.delete(save=False)
	    except:
	    	pass  # when new file then we do nothing, normal case
	    super().save(*args, **kwargs)

class Product_Movement(models.Model):
	Product_Name 		= models.ForeignKey(Products, null=True, blank=True, on_delete=models.CASCADE)
	Quantity			= models.FloatField(max_length=10, null=True, help_text='quantity in nos/sets/kgs/ltrs/bags')
	Movement 			= models.CharField(max_length=15, null=True, choices=(('Added', 'Added'), ('Deleted', 'Deleted')))	
	Date 				= models.DateTimeField(blank=True, null=True, help_text='product added/updated date')
	Stock				= models.FloatField(max_length=10, null=True, blank=True, help_text='Present Stock')
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL)
	Inward_Ref_PO		= models.ForeignKey('Purchases', null=True, blank=True, on_delete=models.SET_NULL)
	Related_Order 		= models.ForeignKey('Orders.Orders', null=True, blank=True, on_delete=models.SET_NULL)
	Other_Reason 		= models.CharField(max_length=15, null=True, blank=True, choices=(('Damaged', 'Damaged'), ('Scrap', 'Scrap'), ('Missing', 'Missing'), ('Expired', 'Expired')))	
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 

	def __str__(self):
		return str(self.Product_Name.Product_Name)+'-'+str(self.Date)+'-'+str(self.Quantity)+'-'+str(self.Movement)+'- Stock/'+str(self.Stock)

class Product_Price(models.Model):
	Product_Name 		= models.ForeignKey(Products, null=True, blank=True, on_delete=models.CASCADE)
	Unit_Price			= models.FloatField(max_length=15, blank=True, null=True, help_text='each unit price excluding all taxes')
	GST					= models.FloatField(max_length=5, blank=True, null=True, help_text='GST in % such as 12, 18 etc')
	HSN_Code			= models.IntegerField(blank=True, null=True, help_text='HSN/SAC Code for this product')
	CESS				= models.FloatField(max_length=5, blank=True, null=True, help_text='CESS in % if applicable')	
	Other_Taxes			= models.FloatField(max_length=5, blank=True, null=True, help_text='specify if any other taxes in % only')
	TDS_Deductions		= models.FloatField(max_length=5, blank=True, null=True, help_text='specify if TDS deductions in % only')
	HSN_Code			= models.FloatField(max_length=10, blank=True, null=True, help_text='HSN/SAC Code for this product')
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 

	def __str__(self):
		return str(self.Product_Name.Product_Name)+'-'+str(self.Unit_Price)

class Purchase_TC(models.Model): 
	Terms_and_Condition1 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition2 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition3 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition4 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition5 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition6 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition7 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition8 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')

	def __str__(self):
		return str(self.Terms_and_Condition1)

class PO_Terms_Conditions(models.Model): #for particular PO
	PO_No	    	 	 = models.ForeignKey('Purchases', null=True, blank=True, on_delete=models.CASCADE)
	Terms_and_Condition1 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition2 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition3 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition4 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition5 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition6 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition7 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	Terms_and_Condition8 = models.CharField(max_length=70, null=True, blank=True, help_text='optional')
	# Additional_Note 	 = models.TextField(max_length=140, null=True, blank=True, help_text='If want to put any additional note you can put here')

	def __str__(self):
		return str(self.PO_No)+'-'+str(self.Terms_and_Condition1)

class PO_Items(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	PO_No 		    	= models.ForeignKey('Purchases', null=True, blank=True, on_delete=models.CASCADE)
	Add_Item   			= models.ForeignKey(Product_Price, null=True, on_delete=models.SET_NULL)
	Quantity			= models.FloatField(max_length=10, null=True)
	
	def __str__(self):
		return str(self.Add_Item.Product_Name)+'-'+str(self.Quantity)

class Copy_PO_Items(models.Model):
	PO_No 		    	= models.ForeignKey('Purchases', null=True, blank=True, on_delete=models.CASCADE)
	Item_From_Product   = models.ForeignKey(PO_Items, null=True, blank=True, on_delete=models.SET_NULL)
	Item_Description 	= models.TextField(max_length=1000, null=True, blank=True, help_text='Item description')
	HSN_Code			= models.IntegerField(blank=True, null=True, help_text='HSN/SAC Code for this product')
	Quantity			= models.FloatField(max_length=10, null=True, help_text='quantity')
	UOM 				= models.CharField(max_length=15, null=True, choices=uom)
	Unit_Price			= models.FloatField(max_length=15, blank=True, null=True, help_text='each unit price excluding all taxes')
	GST					= models.FloatField(max_length=5, blank=True, null=True, help_text='GST in % such as 12, 18 etc')
	CESS				= models.FloatField(max_length=5, blank=True, null=True, help_text='CESS in % if applicable')
	TDS_Deductions		= models.FloatField(max_length=5, blank=True, null=True, help_text='specify if TDS deductions in % only')
	Other_Taxes			= models.FloatField(max_length=5, blank=True, null=True, help_text='specify if any other taxes in % only')
	
	def __str__(self):
		return str(self.PO_No)+'-'+str(self.Item_Description)

class Vendor_Payment_Status(models.Model):
	PO_No 				= models.ForeignKey('Purchases', null=True, blank=True, on_delete=models.CASCADE)
	Invoice_No 			= models.ForeignKey('Vendor_Invoices', null=True, blank=True, on_delete=models.SET_NULL)
	Paid_Amount			= models.FloatField(max_length=20, null=True, blank=True, help_text='received payment against this order')
	Payment_Type 		= models.CharField(max_length=20, null=True, blank=True, choices=(('Due', 'Due'), ('Advance', 'Advance')))
	Payment_Date 		= models.DateTimeField(blank=True, null=True, help_text='payment received date')
	As_Advance_Amount	= models.FloatField(max_length=20, null=True, blank=True, help_text='If any as advance after clear all bills')
	Next_Commitment_Date= models.DateField(blank=True, null=True, help_text='specify if any next payment commitment date')
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 

	def __str__(self):
		return str(self.PO_No)+'-'+str(self.Paid_Amount)+'-'+str(self.Payment_Date)

class Purchases(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL, help_text='leave empty if product meant for many projects') 		
	Purchase_Details   	= models.TextField(max_length=1000, null=True, blank=True, help_text='overall PO short description')
	Order 		        = models.ForeignKey('Orders.Orders', null=True, blank=True, on_delete=models.SET_NULL)
	PO_From 			= models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL, related_name='pofrom')
	Vendor 				= models.ForeignKey(VendDt, null=True, blank=True, on_delete=models.SET_NULL)
	Vendor_Contact		= models.ForeignKey(VendContDt, null=True, blank=True, on_delete=models.SET_NULL)
	Shipping_To 		= models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL, related_name='shipto')
	Terms_and_Conditions= models.ForeignKey(PO_Terms_Conditions, null=True, blank=True, on_delete=models.SET_NULL)		
	PO_No_Format 		= models.ForeignKey(No_Formats, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to=models.Q(No_Format_Related_To__in = ['PO']))
	PO_No 				= models.CharField(max_length=30, blank=True, null=True, unique=True, help_text='PO No') #backend
	PO_No_1				= models.IntegerField(default=0, null=True, blank=True) #backend
	FY 					= models.CharField(max_length=10, blank=True, null=True, help_text='financial year such as 22-23, 23-24 etc..')
	PO_Date 			= models.DateTimeField(blank=True, null=True, help_text='billed date')
	PO_Value			= models.FloatField(max_length=20, null=True, blank=True, help_text='including all taxes')
	Delivery_Date 		= models.DateField(blank=True, null=True, help_text='payment due date')
	Billing_Status		= models.ForeignKey('Vendor_Invoices', null=True, blank=True, on_delete=models.SET_NULL) 	
	Payment_Status		= models.ForeignKey(Vendor_Payment_Status, null=True, blank=True, on_delete=models.SET_NULL)
	Delivery_Status		= models.ForeignKey('PO_Delivery_Status', null=True, blank=True, on_delete=models.SET_NULL)
	Due_Amount			= models.FloatField(max_length=20, null=True, blank=True, help_text='Due amount till date against billed')
	Warranty_In 		= models.CharField(max_length=20, blank=True, null=True, choices=(('Month', 'Months'), ('Year', 'Years'), ('Day', 'Days')))
	Warranty			= models.FloatField(max_length=10, blank=True, null=True, help_text='such as 1, 2, 3.. months/years/days')	
	Payment_Term_1 		= models.CharField(max_length=60, blank=True, null=True,  help_text='payment terms')
	Payment_Term_2 		= models.CharField(max_length=60, blank=True, null=True,  help_text='payment term - optional')
	Packing_and_Forwarding = models.CharField(max_length=20, blank=True, null=True, choices=(('Inclusive', 'Inclusive'), ('Excluded', 'Excluded')))
	Remarks 			= models.TextField(max_length=500, null=True, blank=True)
	Lock_Status			= models.BooleanField(default=False, help_text='mark if wnat to lock invoice to avoid editing')
	Is_Billed			= models.BooleanField(default=False) #backend	
	Payment_Final_Status= models.BooleanField(default=False)
	Final_Status		= models.BooleanField(default=False)
	ds					= models.BooleanField(default=True)

	def __str__(self):
		return str(self.PO_No)+'-'+str(self.Vendor.Supplier_Name)+'-'+str(self.PO_Value)

class Vendor_Invoices(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
	PO_No 		        = models.ForeignKey(Purchases, null=True, on_delete=models.CASCADE)
	Invoice_No 			= models.CharField(max_length=30, null=True, unique=True, help_text='vendor issued invoice no against po') #backend
	Invoice_Date 		= models.DateTimeField(null=True, help_text='billed date')
	Invoice_Amount		= models.FloatField(max_length=20, null=True, help_text='including all taxes')
	GST_Amount			= models.FloatField(max_length=10, blank=True, null=True, help_text='only GST Amount, if no GST enter 0')
	CESS_Amount			= models.FloatField(max_length=10, blank=True, null=True, help_text='CESS Amount')	
	Due_Amount			= models.FloatField(max_length=20, null=True, blank=True, help_text='Due amount till date against billed')
	Payment_Status		= models.ForeignKey(Vendor_Payment_Status, null=True, blank=True, on_delete=models.SET_NULL)
	Credit_Days			= models.IntegerField(default=0, null=True, blank=True, help_text='credit in days such as 0, 15, 30, 60 etc..')
	Payment_Cleared_Date= models.DateTimeField(blank=True, null=True, help_text='date of payment clearing')
	Payment_Over_Due_Days= models.IntegerField(null=True, blank=True, help_text='overdue in days such as 0, 30 etc..')
	Payment_Due_Date 	= models.DateField(blank=True, null=True, help_text='payment due date')
	Attach				= models.FileField(upload_to='vendorinvoices/', blank=True, null=True, help_text='attach order copy if available')

	def __str__(self):
		return str(self.Invoice_No)+'-'+str(self.Invoice_Amount)


class PO_Delivery_Status(models.Model): 
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
	PO_No 		        = models.ForeignKey(Purchases, null=True, on_delete=models.CASCADE)
	Delivery_Date 		= models.DateTimeField(null=True, help_text='delivery date')
	Is_Delivered_Fully  = models.BooleanField(default=False, help_text='mark it if all material as per PO delevered')
	Want_To_Close_PO  	= models.BooleanField(default=False, help_text='mark it if not want futher delivery with this PO')	
	Next_Commitment_Date= models.DateField(blank=True, null=True, help_text='yyyy-mm-dd')
	Remarks 			= models.TextField(max_length=500, null=True, blank=True, help_text='specify if any comments or remarks on delivery')
	Attach				= models.FileField(upload_to='vendorinvoices/', blank=True, null=True, help_text='attach if any delivery challan against PO delivery from vendor')

	def __str__(self):
		return str(self.PO_No)+'-'+str(self.Delivery_Date)+'-'+str(self.Want_To_Close_PO)


