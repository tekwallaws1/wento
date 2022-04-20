from django.db import models
from django.contrib.auth.models import User

class Account(models.Model): 
	Name 					= models.CharField(max_length=50, unique=True, null=True, help_text='Full Name')
	Short_Name				= models.CharField(max_length=15, null=True, unique=True, blank=True, help_text='Nick Name or Short Name')
	E_Id					= models.CharField(max_length=15, blank=True, unique=True, null=True, help_text='Employee ID')
	Designation 			= models.CharField(max_length=100, null=True, help_text='Employee Designation')
	Department 				= models.CharField(max_length=100, null=True, blank=True, help_text='Department')
	Phone_Number 			= models.CharField(max_length=10, null=True, help_text='10 Digit Main Phone Number')
	User_Name				= models.CharField(max_length=30, null=True, unique=True, help_text='Allocated User Name')

	def __str__(self):
		return str(self.Name)