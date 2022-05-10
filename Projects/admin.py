from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Projects)
@admin.register(CompanyDetails)
@admin.register(CustDt)
@admin.register(VendDt)
@admin.register(CustContDt)
@admin.register(VendContDt)

class ProjectsAdmin(ImportExportModelAdmin):
	pass