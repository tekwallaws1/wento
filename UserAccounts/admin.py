from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Account)
@admin.register(EMP_More_Dtls)
@admin.register(EMP_Bank_Dtls)
@admin.register(Empl_Salaries)
@admin.register(Empl_Salary_Revisions)
@admin.register(Page_Permissions)
@admin.register(Pages)
@admin.register(Page_Modes)

class AccountsAdmin(ImportExportModelAdmin):
	pass
