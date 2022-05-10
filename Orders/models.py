from django.db import models
from Projects.models import *
from UserAccounts.models import *
# Create your models here. 

order_by = (('By PO', 'By PO'), ('By Mail', 'By Mail'), ('By Phone', 'By Phone'))

class Sales_Product(models.Model):
	Order_No 			= models.ForeignKey('Orders', null=True, blank=True, on_delete=models.SET_NULL)
	Product_Description = models.TextField(max_length=1000, null=True, unique=True, help_text='product details')
	Quantity			= models.IntegerField(null=True, blank=True, help_text='Quantity')
	UOM					= models.CharField(max_length=20, blank=True, unique=True, null=True, help_text='units such as Nos, sets etc...')
	Unit_Price			= models.FloatField(max_length=15, blank=True, null=True, help_text='each UOM/unit price excluding GST/Tax')
	GST					= models.FloatField(max_length=10, blank=True, null=True, help_text='GST in % such as 12, 18 etc')
	TDS					= models.FloatField(max_length=10, blank=True, null=True, help_text='If any Service Tax/TDS applicable')

	def __str__(self):
		return str(self.Order_No.Order_No)+'-'+self.Product_Description

class Orders(models.Model):
	user				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL) 
	Customer_Name 		= models.ForeignKey(CustDt, null=True, on_delete=models.SET_NULL)
	Order_Details   	= models.TextField(max_length=1000, null=True, blank=True, help_text='overall order short description')
	Add_Product   		= models.ForeignKey(Sales_Product, null=True, blank=True, on_delete=models.SET_NULL)
	Order_Value			= models.FloatField(max_length=20, null=True, blank=True, help_text='order value or estimated value excluding taxes')
	Order_Type 			= models.CharField(max_length=20, blank=True, null=True, choices=(('Confirmed', 'Confirmed'), ('Pipeline', 'Pipeline')))
	Order_Received_Date = models.DateTimeField(blank=True, null=True, help_text='Received Order Date')
	Order_Reference_Person	= models.ForeignKey(CustContDt, on_delete=models.SET_NULL, null=True, help_text='order reference person name')
	Order_Through 		= models.CharField(max_length=20, choices=order_by, blank=True, null=True)
	Status				= models.BooleanField(default=False, help_text='tick if completed')
	Attach				= models.FileField(upload_to='orders/', blank=True, null=True, help_text='attach order copies if available')
	ds					= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Order_No)+'-'+self.Company_Name.Name+'-'+str(self.Order_Value)

