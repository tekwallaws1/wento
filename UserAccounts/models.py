from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
	Name					= models.CharField(max_length=30, null=True, help_text='Full Name')
	Nick_Name				= models.CharField(max_length=10, null=True, help_text='Nick Name or Short Name')
	Phone_Number 			= models.CharField(max_length=10, null=True, help_text='10 Digit Phone Number')
	Designation 			= models.CharField(max_length=100, null=True, blank=True, help_text='Leave as blank if not available')
	Department 				= models.CharField(max_length=100, null=True, blank=True, help_text='Leave as blank if not available')
	Employee_Id				= models.CharField(max_length=15, blank=True, unique=True, null=True, help_text='Leave as blank if not available')
	Upload_Photo			= models.FileField(upload_to='employeephotos/', blank=True, help_text='Upload Your Photo')
	user 					= models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
	ds						= models.BooleanField(default=True)

	def save(self, *args, **kwargs):
	    try:
	        this = Account.objects.get(id=self.id)
	        if this.Upload_Photo != self.Upload_Photo:
	        	this.Upload_Photo.delete(save=False)
	    except:
	    	pass  # when new photo then we do nothing, normal case
	    super().save(*args, **kwargs)

	def __str__(self):
		return str(self.Nick_Name) 

class Permissions(models.Model):
	user 					= models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
	Admin					= models.BooleanField(default=False, help_text='Admin Permissions - All Access')
	Main_Dashboard			= models.BooleanField(default=False, help_text='Orders, Payments and Its Statestics View Permissions')
	Proposals_Dashboard		= models.BooleanField(default=False, help_text='Proposal Dashboard View Permissions')
	Expenses_Dashboard		= models.BooleanField(default=False, help_text='Expenses Dashboard View Permissions')

	Create					= models.BooleanField(default=False, help_text='Create Permissions for Selected Dashboards')
	Edit					= models.BooleanField(default=False, help_text='Edit Permissions for Selected Dashboards')
	Delete					= models.BooleanField(default=False, help_text='Delete Permissions for Selected Dashboards')

	def __str__(self):
		return str(self.user.username)+'-'+str(self.Admin)