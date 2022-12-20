from UserAccounts.models import Account, Page_Modes, Pages, Page_Permissions
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

 

def firmname(request, var):
	if var != None:
		fm = CompanyDetails.objects.filter(Short_Name = var, ds=True).last()
		return {'fm':fm.Short_Name}
	else:
		fm = CompanyDetails.objects.filter(ds=True, Address_Type='Billing') #Before Select all companies should load
		return {'fm':fm}


def projectname(request, var):
	# if var != None:
	# 	pj = Projects.objects.filter(Short_Name = var, Status='Active', ds=True).last()
	# else:
	# 	pj = Projects.objects.filter(Status='Active', ds=True) #Before Select Project All should load
	# return {'pj':pj}

	if var != None and var != 'All':
		pj = Projects.objects.filter(Short_Name = var, Status='Active', ds=True).last()
		return {'pj':pj}
	elif var == 'All':
		return {'pj':'All'}
	else:
		pj = Projects.objects.filter(Status='Active', ds=True)
		return {'pj':pj}

def projectname1(request, var, firm):
	pj = Projects.objects.filter(Status='Active', ds=True, RC=firm)
	return {'pj':pj}

def profiledata(request):
	if request.user.username:  
		try:
			account = Account.objects.filter(user__username = request.user.username, user__is_active = True).last()
			if account.Upload_Photo:
				pic_url =  '/media/'+str(account.Upload_Photo)+'/'
			else:
				pic_url =  '/media/employes/sss-logo.png/'

			return {'name':account.Name,'designation':account.Designation, 'profilepic_url':pic_url}
		except Account.DoesNotExist:
			return {'name':'Developer', 'designation':'Developer', 'profilepic_url':'/media/employes/sss-logo.png/'}
	else:
		return {'designation':'Unknown', 'profilepic_url':'/media/employes/sss-logo.png/'}


def customer_updateledger(request, cat, fnc, pdata, inst):
	firm = inst.Order.RC.Short_Name if cat == 'custinv' else inst.Order_No.RC.Short_Name
	if fnc == 'edit':
		updt = Customer_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last() if cat == 'custinv' else Customer_Ledger.objects.filter(Row_ID=inst.id, Credit__isnull=False).last()
		updt.delete()
		
	if fnc == 'create' or fnc == 'edit': 
		lgr_0 = Customer_Ledger.objects.filter(RC__Short_Name=firm, Lock_Status=1).order_by('Date', 'Sr_No').last()
		if cat == 'custinv':
			lgr_cust = Customer_Ledger.objects.filter(RC__Short_Name=firm, Lock_Status=1, Partner = inst.Order.Customer_Name.Customer_Name).order_by('Date', 'Sr_No').last()
		else:
			lgr_cust = Customer_Ledger.objects.filter(RC__Short_Name=firm, Lock_Status=1, Partner = inst.Order_No.Customer_Name.Customer_Name).order_by('Date', 'Sr_No').last()			
		
		bal = lgr_0.Bal_All if lgr_0 != None else 0
		bal_cust = lgr_cust.Bal_Customer if lgr_cust != None else 0
		srno = lgr_0.Sr_No if lgr_0 != None else 0
		dt = inst.Invoice_Date if cat == 'custinv' else inst.Payment_Date
		
		if cat == 'custinv':		
			create = Customer_Ledger.objects.create(
				Date = inst.Invoice_Date,
				RC = inst.Order.RC,
				Related_Project = pdata['pj'], 
				Ref_No = inst.Invoice_No,
				Partner = inst.Order.Customer_Name.Customer_Name,
				Debit = inst.Invoice_Amount,
				Lock_Status = 1,
				Row_ID = inst.id)
		else:
			create = Customer_Ledger.objects.create(
				Date = inst.Payment_Date,
				RC = inst.Order_No.RC,
				Related_Project = pdata['pj'], 
				Ref_No = inst.id,
				Partner = inst.Order_No.Customer_Name.Customer_Name,
				Credit = inst.Received_Amount,
				Lock_Status = 1,
				Row_ID = inst.id)

	else:
		if cat == 'custinv':
			updt = Customer_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last()
			srno_del = updt.Sr_No
			updt.delete()
		else:
			updt = Customer_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Credit__isnull=False).last()
			srno_del = updt.Sr_No
			updt.delete()


	if fnc == 'create' or fnc == 'edit':
		if lgr_0 == None or (dt.date() >= lgr_0.Date):
			lgr_1 = Customer_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last() if cat == 'custinv' else Customer_Ledger.objects.filter(Row_ID=inst.id, Credit__isnull=False).last()
			lgr_1.Sr_No = srno + 1
			lgr_1.Bal_All = float(bal) + inst.Invoice_Amount if cat == 'custinv' else float(bal) - inst.Received_Amount
			lgr_1.save()
		else:
			lg_last = Customer_Ledger.objects.filter(RC__Short_Name=firm, Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg = Customer_Ledger.objects.filter(RC__Short_Name=firm, Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')
			sr_no = lg_last.Sr_No if lg_last != None else 0
			bal = lg_last.Bal_All if lg_last != None else 0
			for k in lg:
				sr_no = sr_no + 1
				k.Sr_No = sr_no
				if k.Debit != None:
					bal = bal + k. Debit
				else:
					if k.Credit:
						bal = bal - k.Credit
				k.Bal_All = bal
				k.save()

		if lgr_cust == None or (dt.date() >= lgr_cust.Date):
			lgr_cust1 = Customer_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last() if cat == 'custinv' else Customer_Ledger.objects.filter(Row_ID=inst.id, Credit__isnull=False).last()
			lgr_cust1.Bal_Customer = float(bal_cust) + inst.Invoice_Amount if cat == 'custinv' else float(bal_cust) - inst.Received_Amount
			lgr_cust1.save()
		
		else:

			if cat == 'custinv':
				lg_cust_last = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order.Customer_Name.Customer_Name).filter(Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
				lg_cust = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order.Customer_Name.Customer_Name).filter(Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')
			else:
				lg_cust_last = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
				lg_cust = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')

			bal_cust = lg_cust_last.Bal_Customer if lg_cust_last != None else 0
			for k in lg_cust:
				print('k.Ref_No', k.Ref_No)
				if k.Debit != None:
					bal_cust = bal_cust + k.Debit
				else:
					if k.Credit:
						bal_cust = bal_cust - k.Credit
				k.Bal_Customer = bal_cust
				print('k.Bal_Customer', k.Bal_Customer)
				k.save()
	else:
		lg_last = Customer_Ledger.objects.filter(RC__Short_Name=firm, Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
		lg = Customer_Ledger.objects.filter(RC__Short_Name=firm, Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')
		sr_no = lg_last.Sr_No if lg_last != None else 0
		bal = lg_last.Bal_All if lg_last != None else 0
		for k in lg:
			sr_no = sr_no + 1
			k.Sr_No = sr_no
			if k.Debit != None:
				bal = bal + k. Debit
			else:
				if k.Credit:
					bal = bal - k.Credit
			k.Bal_All = bal
			k.save()

		if cat == 'custinv':
			lg_cust_last = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order.Customer_Name.Customer_Name).filter(Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg_cust = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order.Customer_Name.Customer_Name).filter(Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')
		else:
			lg_cust_last = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg_cust = Customer_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')

		bal_cust = lg_cust_last.Bal_Customer if lg_cust_last != None else 0
		
		for k in lg_cust:
			if k.Debit != None:
				bal_cust = bal_cust + k.Debit
			else:
				if k.Credit:
					bal_cust = bal_cust - k.Credit
			k.Bal_Customer = bal_cust
			k.save()


def vendor_updateledger(request, cat, fnc, pdata, inst):
	firm = inst.PO_No.RC.Short_Name
	if fnc == 'edit':
		updt = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Credit__isnull=False).last() if cat == 'vendinv' else Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last()
		updt.delete()
		
	if fnc == 'create' or fnc == 'edit': 
		lgr_0 = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Lock_Status=1).order_by('Date', 'Sr_No').last()
		if cat == 'vendinv':
			lgr_cust = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Lock_Status=1, Partner = inst.PO_No.Vendor.Supplier_Name).order_by('Date', 'Sr_No').last()
		else:
			lgr_cust = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Lock_Status=1, Partner = inst.PO_No.Vendor.Supplier_Name).order_by('Date', 'Sr_No').last()			
		
		bal = lgr_0.Bal_All if lgr_0 != None else 0
		bal_vend = lgr_cust.Bal_Vendor if lgr_cust != None else 0
		srno = lgr_0.Sr_No if lgr_0 != None else 0
		dt = inst.Invoice_Date if cat == 'vendinv' else inst.Payment_Date
		
		if cat == 'vendinv':		
			create = Vendor_Ledger.objects.create(
				Date = inst.Invoice_Date,
				RC = inst.PO_No.RC,
				Related_Project = pdata['pj'], 
				Ref_No = inst.Invoice_No,
				Partner = inst.PO_No.Vendor.Supplier_Name,
				Credit = inst.Invoice_Amount,
				Lock_Status = 1,
				Row_ID = inst.id)
		else:
			create = Vendor_Ledger.objects.create(
				Date = inst.Payment_Date,
				RC = inst.PO_No.RC,
				Related_Project = pdata['pj'], 
				Ref_No = inst.id,
				Partner = inst.PO_No.Vendor.Supplier_Name,
				Debit = inst.Paid_Amount,
				Lock_Status = 1,
				Row_ID = inst.id)

	else:
		if cat == 'vendinv':
			updt = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Credit__isnull=False).last()
			srno_del = updt.Sr_No
			updt.delete()
		else:
			updt = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last()
			srno_del = updt.Sr_No
			updt.delete()


	if fnc == 'create' or fnc == 'edit':
		if lgr_0 == None or (dt.date() >= lgr_0.Date):
			lgr_1 = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Credit__isnull=False).last() if cat == 'vendinv' else Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last()
			lgr_1.Sr_No = srno + 1
			lgr_1.Bal_All = float(bal) + inst.Invoice_Amount if cat == 'vendinv' else float(bal) - inst.Paid_Amount
			lgr_1.save()
		else:
			lg_last = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')
			sr_no = lg_last.Sr_No if lg_last != None else 0
			bal = lg_last.Bal_All if lg_last != None else 0
			for k in lg:
				sr_no = sr_no + 1
				k.Sr_No = sr_no
				if k.Credit != None:
					bal = bal + k. Credit
				else:
					if k.Debit:
						bal = bal - k.Debit
				k.Bal_All = bal
				k.save()

		if lgr_cust == None or (dt.date() >= lgr_cust.Date):
			lgr_cust1 = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Credit__isnull=False).last() if cat == 'vendinv' else Vendor_Ledger.objects.filter(RC__Short_Name=firm, Row_ID=inst.id, Debit__isnull=False).last()
			lgr_cust1.Bal_Vendor = float(bal_vend) + inst.Invoice_Amount if cat == 'vendinv' else float(bal_vend) - inst.Paid_Amount
			lgr_cust1.save()
		
		else:

			if cat == 'vendinv':
				lg_vend_last = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
				lg_vend = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')
			else:
				lg_vend_last = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
				lg_vend = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')

			bal_vend = lg_vend_last.Bal_Vendor if lg_vend_last != None else 0
			for k in lg_vend:
				if k.Credit != None:
					bal_vend = bal_vend + k.Credit
				else:
					if k.Debit:
						bal_vend = bal_vend - k.Debit
				k.Bal_Vendor = bal_vend
				k.save()
	else:
		lg_last = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
		lg = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')
		sr_no = lg_last.Sr_No if lg_last != None else 0
		bal = lg_last.Bal_All if lg_last != None else 0
		for k in lg:
			sr_no = sr_no + 1
			k.Sr_No = sr_no
			if k.Credit != None:
				bal = bal + k. Credit
			else:
				if k.Debit:
					bal = bal - k.Debit
			k.Bal_All = bal
			k.save()

		if cat == 'vendinv':
			lg_vend_last = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg_vend = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')
		else:
			lg_vend_last = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg_vend = Vendor_Ledger.objects.filter(RC__Short_Name=firm, Partner = inst.PO_No.Vendor.Supplier_Name).filter(Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')

		bal_vend = lg_vend_last.Bal_Vendor if lg_vend_last != None else 0
		
		for k in lg_vend: 
			if k.Credit != None:
				bal_vend = bal_vend + k.Credit
			else:
				if k.Debit:
					bal_vend = bal_vend - k.Debit
			k.Bal_Vendor = bal_vend
			k.save()


def permissions(request, pg, mode, firm, proj, user):
	# pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project__Short_Name':proj}
	usr = Account.objects.get(user=request.user)

	if usr.Is_Super_Admin == 1:
		print('l')
		return 1
	if proj != 'All':
		project = Projects.objects.get(Short_Name=proj)
		if Projects.objects.get(Short_Name=proj) in usr.Related_Project.all():
			pass
		else:
			return 0
	else:
		if len(Projects.objects.filter(ds=1, Status='Active', RC__Short_Name=firm)) == len(usr.Related_Project.filter(ds=1, Status='Active', RC__Short_Name=firm)):
			pass
	
	ps = Page_Permissions.objects.filter(user=user, RC__Short_Name=firm)
	pms = None
	if ps:
		if mode == 'View':
			pms = ps.filter(View_Permissions__Page=pg)
		else:
			pms = ps.filter(Edit_Permissions__Page=pg)
	if pms:
		return 1
	else:
		return 0

	# if mode == 'View':
	# 	page = Pages.objects.filter(Mode__Mode='View', RC__Short_Name=firm, Related_Project__Short_Name=proj, Page=pg).last()
	# else:
	# 	page = Pages.objects.filter(Mode__Mode='View', RC__Short_Name=firm, Related_Project__Short_Name=proj, Page=pg).last()
	# ps = Page_Permissions.objects.filter(user=user, RC__Short_Name=firm)
	


		
