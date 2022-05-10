from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta 

# Create your models here.

states = (("Andhra Pradesh","Andhra Pradesh"),("Telangana","Telangana"),("Tamil Nadu","Tamil Nadu"),("Karnataka","Karnataka"),("Maharashtra","Maharashtra"),("Kerala","Kerala"),
	("Chhattisgarh","Chhattisgarh"),("Delhi","Delhi"),("Goa","Goa"),("Gujarat","Gujarat"),("Punjab","Punjab"),("Rajasthan","Rajasthan"),("Haryana","Haryana"),("West Bengal","West Bengal"),("Himachal Pradesh","Himachal Pradesh"),
	("Jammu and Kashmir ","Jammu and Kashmir "),("Jharkhand","Jharkhand"),("Arunachal Pradesh ","Arunachal Pradesh "),("Assam","Assam"),("Bihar","Bihar"),
	("Madhya Pradesh","Madhya Pradesh"),("Manipur","Manipur"),("Meghalaya","Meghalaya"),("Mizoram","Mizoram"),("Nagaland","Nagaland"),("Odisha","Odisha"),
	("Sikkim","Sikkim"),("Tripura","Tripura"),("Uttar Pradesh","Uttar Pradesh"),("Uttarakhand","Uttarakhand"),("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),
	("Chandigarh","Chandigarh"),("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),("Daman and Diu","Daman and Diu"),("Lakshadweep","Lakshadweep"),("Puducherry","Puducherry"))


class CompanyDetails(models.Model):
	Company_Name 			= models.CharField(max_length=40, null=True)
	Address_Line_1			= models.CharField(max_length=40, blank=True, null=True, help_text='Address Line 1')
	Address_Line_2			= models.CharField(max_length=35, blank=True, null=True, help_text='Address Line 2')
	State 					= models.CharField(max_length=50, null=True, choices=states)
	GST_No 					= models.CharField(max_length=15, blank=True, null=True, help_text='Provide If Company under GST')
	Phone_Number_1 			= models.CharField(max_length=20, null=True, help_text='Main Phone Number')
	Phone_Number_2 			= models.CharField(max_length=10, null=True, blank=True, help_text='Optional Phone Number')
	Email 					= models.EmailField(max_length=40, null=True, help_text='Company Contact Mail Address')
	Website 				= models.CharField(max_length=40, blank=True, null=True)
	Address_Type			= models.CharField(max_length=40, blank=True, null=True, choices=(('Billing', 'Billing'),('Shipping', 'Shipping'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')))
	Active_From				= models.DateField(null=True, blank=True, help_text='If leave this, it will take today date') 
	Status 					= models.BooleanField(default = True, help_text='Unmark if Company Address not in Active')
	ds						= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Company_Name)+'-'+str(self.Address_Line_1)+'-'+str(self.Address_Line_2)+'-'+str(self.State)

class Projects(models.Model):
	Project_Name 				= models.CharField(max_length=50, null=True, unique=True, help_text='Project Name Such as Rooftop, Solar Pumps')
	Short_Name					= models.CharField(max_length=15, null=True, unique=True, help_text='Nick Name or Short Name of Project')
	user 						= models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL) #backend
	Date 						= models.DateField(null=True, blank=True, help_text='Project Creation Date')
	Status						= models.CharField(max_length=15, null=True, choices=(('Active','Active'), ('Not Active', 'Not Active')))
	ds							= models.BooleanField(default=True)
	#ds Means if any dataset deleted by user, it will make inactive instaed of delete, because its parent model
	def __str__(self):
		return str(self.Short_Name)

class CustDt(models.Model):
	Customer_Name 			= models.CharField(max_length=50, null=True, help_text='Customer/Company Name')
	Short_Name 				= models.CharField(max_length=15, null=True, help_text='Give Short Name for Customer, Max 15 Characters')
	Address_Line_1			= models.CharField(max_length=40, blank=True, null=True, help_text='Address Line 1')
	Address_Line_2			= models.CharField(max_length=35, blank=True, null=True, help_text='Address Line 2')
	State 					= models.CharField(max_length=50, null=True, choices=states)
	GST_No 					= models.CharField(max_length=15, blank=True, null=True, help_text='Provide If Company under GST')
	Phone_Number_1 			= models.CharField(max_length=20, null=True, help_text='Main Contact Phone Number')
	Phone_Number_2 			= models.CharField(max_length=20, null=True, blank=True, help_text='Optional/Alternative Phone Number')
	Email 					= models.EmailField(max_length=40, null=True, blank=True, help_text='Customer/Company Contact Mail Address')
	Website 				= models.CharField(max_length=40, blank=True, null=True, help_text='Official Website, Format: wwww.xyz.com only')
	Address_Type			= models.CharField(max_length=40, null=True, choices=(('Billing', 'Billing'), ('Shipping', 'Shipping'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')))
	Related_Project			= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL)
	Active_From				= models.DateField(null=True, blank=True, help_text='If leave this, it will take today date')
	Status 					= models.BooleanField(default = True, help_text='Unmark if Company is not in Active')
	Attach_Doc				= models.FileField(upload_to='customers/', blank=True, null=True, help_text='Upload if any reference document')
	ds						= models.BooleanField(default=True)

	def save(self, *args, **kwargs): #if file updated it will delete old file and replace
	    try:
	        this = CustDt.objects.get(id=self.id)
	        if this.Attach_Doc != self.Attach_Doc:
	        	this.Attach_Doc.delete(save=False)
	    except:
	    	pass  # when new file then we do nothing, normal case
	    super().save(*args, **kwargs)

	def __str__(self):
		return str(self.Customer_Name)+'-'+str(self.Address_Line_1)+'-'+str(self.Address_Line_2)+'-'+str(self.State)+'-'+str(self.Address_Type)

class VendDt(models.Model):
	Supplier_Name 			= models.CharField(max_length=50, null=True, help_text='Vendor/Supplier Name')
	Short_Name 				= models.CharField(max_length=15, null=True, help_text='Give Short Name for Supplier, Max 15 Characters')
	Address_Line_1			= models.CharField(max_length=40, blank=True, null=True, help_text='Address Line 1')
	Address_Line_2			= models.CharField(max_length=35, blank=True, null=True, help_text='Address Line 2')
	State 					= models.CharField(max_length=50, null=True, choices=states)
	GST_No 					= models.CharField(max_length=15, blank=True, null=True, help_text='Provide If Company under GST')
	Phone_Number_1 			= models.CharField(max_length=20, null=True, help_text='Main Contact Phone Number')
	Phone_Number_2 			= models.CharField(max_length=20, null=True, blank=True, help_text='Optional/Alternative Phone Number')
	Email 					= models.EmailField(max_length=40, null=True, blank=True, help_text='Customer/Company Contact Mail Address')
	Website 				= models.CharField(max_length=40, blank=True, null=True, help_text='Official Website, Format: wwww.xyz.com only')
	Address_Type			= models.CharField(max_length=40, null=True, choices=(('Billing', 'Billing'), ('Shipping', 'Shipping'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')))
	Related_Project			= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL)
	Supplier_Product_Details= models.TextField(max_length=200, null=True, blank=True, help_text='Supplier Product Details - Shortly')
	Status 					= models.BooleanField(default = True, help_text='Unmark if Supplier is not in Active')
	Active_From				= models.DateField(null=True, blank=True, help_text='If leave this, it will take today date') 
	Attach_Doc				= models.FileField(upload_to='vendors/', blank=True, null=True, help_text='Upload if any reference document')
	ds						= models.BooleanField(default=True)

	def save(self, *args, **kwargs):
	    try:
	        this = VendDt.objects.get(id=self.id)
	        if this.Attach_Doc != self.Attach_Doc:
	        	this.Attach_Doc.delete(save=False)
	    except:
	    	pass  # when new file then we do nothing, normal case
	    super().save(*args, **kwargs)

	def __str__(self):
		return str(self.Supplier_Name)+'-'+str(self.Address_Line_1)+'-'+str(self.Address_Line_2)+'-'+str(self.State)+'-'+str(self.Address_Type)

class CustContDt(models.Model):
	Customer_Name 			= models.ForeignKey(CustDt, null=True, blank=True, on_delete=models.CASCADE)
	Contact_Person 			= models.CharField(max_length=30, null=True, help_text='Contact Person Name')
	Phone_Number_1 			= models.CharField(max_length=20, null=True, help_text='Main Contact Phone Number')
	Phone_Number_2 			= models.CharField(max_length=20, null=True, blank=True, help_text='Optional/Alternative Phone Number')
	Email 					= models.EmailField(max_length=50, null=True, blank=True, help_text='Contact Person Email')
	Designation 			= models.CharField(max_length=30, null=True, blank=True, help_text='Specify if any')
	Department 				= models.CharField(max_length=30, null=True, blank=True, help_text='Specify if any')
	Other_Info 				= models.TextField(max_length=200, null=True, blank=True, help_text='Specify if want to give extra info.')
	ds						= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Customer_Name)+'-'+str(self.Contact_Person)

class VendContDt(models.Model):
	Supplier_Name 			= models.ForeignKey(VendDt, null=True, on_delete=models.CASCADE)
	Contact_Person 			= models.CharField(max_length=30, null=True, help_text='Contact Person Name')
	Phone_Number_1 			= models.CharField(max_length=20, null=True, help_text='Main Contact Phone Number')
	Phone_Number_2 			= models.CharField(max_length=20, null=True, blank=True, help_text='Optional/Alternative Phone Number')
	Email 					= models.EmailField(max_length=50, null=True, blank=True, help_text='Contact Person Email')
	Designation 			= models.CharField(max_length=30, null=True, blank=True, help_text='Specify if any')
	Department 				= models.CharField(max_length=30, null=True, blank=True, help_text='Specify if any')
	Other_Info 				= models.TextField(max_length=200, null=True, blank=True, help_text='Specify if want to give extra info.')
	ds						= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Supplier_Name)+'-'+str(self.Contact_Person)


