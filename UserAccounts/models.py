from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings

class Account(models.Model):
	Name					= models.CharField(max_length=30, null=True, help_text='full name of the employee including sir name')
	Nick_Name				= models.CharField(max_length=10, null=True, help_text='short calling name or nick name')
	Gender                  = models.CharField(max_length=10, null=True, blank=True, choices=(('Male', 'Male'),('Female','Female')))
	Phone_Number 			= models.CharField(max_length=10, null=True, help_text='contact number')
	Designation 			= models.CharField(max_length=100, null=True, blank=True, help_text='leave as blank if not available')
	Department 				= models.CharField(max_length=100, null=True, blank=True, help_text='leave as blank if not available')
	Employee_Id				= models.CharField(max_length=15, blank=True, unique=True, null=True, help_text='employee id or serial number')
	Relationship 			= models.CharField(max_length=20, null=True, blank=True, choices=(('Permanent', 'Permanent'), ('Contract', 'Contract')))
	Joining_Date 			= models.DateField(null=True, blank=True, help_text='date of joining')
	Email					= models.EmailField(max_length=50, blank=True, null=True, help_text='official email or personal email')
	Support					= models.CharField(max_length=20, null=True, blank=True, choices=(('Online', 'Online'), ('Field', 'Field'), ('Offline', 'Offline')))
	Upload_Photo			= models.FileField(upload_to='employes/', blank=True, help_text='upload employee photo')
	user 					= models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	Status					= models.BooleanField(default=True, help_text='unmark if he is not active/leave organisation')
	ds						= models.BooleanField(default=True)
	Sr_No					= models.IntegerField(blank=True, unique=True, null=True, help_text='employee id only serial number')

	class Meta:
		ordering = ['Sr_No']

	def save(self, *args, **kwargs):
	    try:
	        this = Account.objects.get(id=self.id)
	        if this.Upload_Photo != self.Upload_Photo:
	        	this.Upload_Photo.delete(save=False)
	    except:
	    	pass  # when new photo then we do nothing, normal case
	    super().save(*args, **kwargs)

	def __str__(self):
		return str(self.Name)+'-'+str(self.Employee_Id)

class EMP_More_Dtls(models.Model):
	Employee 			= models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
	DOB 				= models.DateField(null=True, blank=True, help_text='date of birth')
	# Father_Name 		= models.CharField(max_length=50, null=True, blank=True, help_text='employee father name')
	Alternative_Phone	= models.CharField(max_length=10, null=True, blank=True, help_text='alternative phone number')	
	Aadhaar_No 			= models.CharField(max_length=12, unique=True, null=True, blank=True, help_text='aadhaar no')
	PAN_No 				= models.CharField(max_length=10, unique=True, null=True, blank=True, help_text='pan card no')
	Upload_Aadhaar		= models.FileField(upload_to='employes/aadhaar/', blank=True, help_text='upload adhaar copy')
	Upload_PAN			= models.FileField(upload_to='employes/pan/', blank=True, help_text='upload pan copy')
	Upload_Resume		= models.FileField(upload_to='employes/resumes/', blank=True, help_text='upload pan copy')

	def save(self, *args, **kwargs):
	    try:
	        this = EMP_More_Dtls.objects.get(id=self.id)
	        if this.Upload_Aadhaar != self.Upload_Aadhaar:
	        	this.Upload_Aadhaar.delete(save=False)
	        if this.Upload_PAN != self.Upload_PAN:
	        	this.Upload_PAN.delete(save=False)
	        if this.Upload_Resume != self.Upload_Resume:
	        	this.Upload_Resume.delete(save=False)
	    except:
	    	pass 
	    super().save(*args, **kwargs)

	# def delete(self, *args, **kwargs):
	#    os.remove(os.path.join(settings.MEDIA_ROOT, self.qr_code.name))
	#    super().delete(*args, **kwargs)

	def __str__(self):
		return str(self.Employee)

class EMP_Bank_Dtls(models.Model):
	Employee 				= models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
	Account_No 				= models.CharField(max_length=40, null=True, unique=True, help_text='bank account number')
	Bank_Name 				= models.CharField(max_length=30, null=True, help_text='bank Name')
	Branch 					= models.CharField(max_length=40, null=True, blank=True, help_text='bank branch details')
	IFSC_Code 				= models.CharField(max_length=11, null=True, blank=True, help_text='bank IFSC code')
	Account_Type			= models.CharField(max_length=20, null=True, choices=(('Company', 'Company'), ('Personal', 'Personal')))
	Status					= models.BooleanField(default=True, help_text='active status')

	def __str__(self):
		return str(self.Employee)+'-'+str(self.Account_No)

class EMP_End_Dtls(models.Model):
	Employee 			= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
	Releaving_Date 		= models.DateField(null=True, blank=True, help_text='date of releaving')
	Remarks 			= models.TextField(max_length=500, null=True, blank=True, help_text='remarks or conclusion about employee')

	def __str__(self):
		return str(self.Employee)+'-'+str(self.Releaving_Date)

class Permissions(models.Model):
	user 					= models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
	Admin					= models.BooleanField(default=False, help_text='Admin Permissions - All Access')
	Main_Dashboard			= models.BooleanField(default=False, help_text='Orders, Payments and Its Statestics View Permissions')
	Proposals_Dashboard		= models.BooleanField(default=False, help_text='Proposal Dashboard View Permissions')
	Expenses_Dashboard		= models.BooleanField(default=False, help_text='Expenses Dashboard View Permissions')

	Create					= models.BooleanField(default=False, help_text='Create Permissions for Selected Dashboards')
	Edit					= models.BooleanField(default=False, help_text='Edit Permissions for Selected Dashboards')
	Delete					= models.BooleanField(default=False, help_text='Delete Permissions for Selected Dashboards')
	# Only_Expenses			= models.BooleanField(default=False, help_text='Give perrmission to only expenses entry and see')

	def __str__(self):
		return str(self.user.username)+'-'+str(self.Admin)

class Empl_Salaries(models.Model):
	Employ_Name 			= models.ForeignKey(Account, null=True, unique=True, on_delete=models.SET_NULL)
	Gross_Salary 			= models.IntegerField( null=True, help_text='gross salary or CTC')
	Basic		 			= models.IntegerField( null=True, help_text='basic salary as per govt norms')
	HRA						= models.FloatField(max_length=10, null=True, blank=True, help_text='house rent allowance, 40% of basic')
	Other_Allowances 		= models.FloatField(max_length=10, null=True, blank=True, help_text='other allowances')
	Net_Salary 				= models.IntegerField(null=True, blank=True, help_text='you can give it or we will calculate')
	PF_Amount 				= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='total 4% of gross, 0.75% employee, 3.25% employer')
	ESI_Amount 				= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='total 24% of basic, 12% employee, 12% employer')
	Professional_Tax 		= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='PT deductions if eligible, <15K 0, 15-20K 150, >15K 200 of gross')
	UAN_Number				= models.CharField(max_length=12, null=True, blank=True, help_text='PF/UAN number if eligible')
	ESI_Number				= models.CharField(max_length=10, null=True, blank=True, help_text='ESI number if eligible')
	PAN_Number				= models.CharField(max_length=10, null=True, blank=True, help_text='PAN card number')
	Aadhaar_Number			= models.CharField(max_length=12, null=True, blank=True, help_text='PAN card number')
	PF_Eligibility			= models.BooleanField(default=True)
	Is_Providing_PF_Employer_Share	= models.BooleanField(default=True)
	ESI_Eligibility			= models.BooleanField(default=True)
	OT_Eligibility			= models.BooleanField(default=False)
	Effective_From 			= models.DateField(null=True, blank=True, help_text='salary effective from')
	Next_Revision_Date 		= models.DateField(null=True, blank=True, help_text='salary next revision date, if leave it as blank, it will take a year after date')
	Revision_Status			= models.BooleanField(default=False, help_text='mark if revised salary in his employement history')
	Status					= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Employ_Name)+'-'+str(self.Gross_Salary)

class Empl_Salary_Revisions(models.Model):
	Employ_Name 			= models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
	Previous_Date 			= models.DateField(null=True, blank=True, help_text='salary revision date')
	Effective_From 			= models.DateField(null=True, help_text='salary revision effective from')
	Previous_Gross			= models.IntegerField(null=True, blank=True, help_text='revised gross salary or CTC')
	Revised_Gross 			= models.IntegerField(null=True, help_text='revised gross salary or CTC')
	Previous_Basic			= models.IntegerField(null=True, blank=True, help_text='revised basic salary if revised, otherwise it will take previous basic')
	Revised_Basic			= models.IntegerField(null=True, blank=True, help_text='revised basic salary if revised, otherwise it will take previous basic')
	Next_Revision_Date 		= models.DateField(null=True, blank=True, help_text='salary next revision date, if leave it as blank, it will take a year after date')
	Status					= models.BooleanField(default=True, help_text='active status')

	def __str__(self):
		return str(self.Employ_Name)+'-'+str(self.Effective_From)+'-'+str(self.Revised_Gross)
