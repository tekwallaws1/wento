from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Account)
@admin.register(Permissions)

class AccountsAdmin(ImportExportModelAdmin):
	pass
