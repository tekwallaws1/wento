from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Projects)

class ProjectsAdmin(ImportExportModelAdmin):
	pass