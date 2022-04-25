from django.db import models
from django.contrib.auth.models import User
# Create your models here.


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


