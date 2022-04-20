from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Account)

class AccountsAdmin(ImportExportModelAdmin):
	pass
