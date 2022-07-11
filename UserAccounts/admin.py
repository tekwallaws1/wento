from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Account)
@admin.register(Permissions)
@admin.register(EMP_More_Dtls)
@admin.register(EMP_Bank_Dtls)

class AccountsAdmin(ImportExportModelAdmin):
	pass
