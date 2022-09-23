from UserAccounts.models import Account
from django.contrib.auth.models import User
from .models import Projects, Customer_Ledger, Vendor_Ledger

def call_i(request):
	pass

def projectname(request, var):
	if var != None:
		pj = Projects.objects.filter(Short_Name = var, Status='Active', ds=True).last()
	else:
		pj = Projects.objects.filter(Status='Active', ds=True) #Before Select Project All should load

	# if request.user.username:
	# 	carry_msg_update = Carry_Msg.objects.filter(user__user__username = request.user.username).last()
	# 	carry_msg_update.Status = 0
	# 	carry_msg_update.save()

	return {'pj':pj}

def profiledata(request):
	if request.user.username:  
		try:
			account = Account.objects.get(user__username = request.user.username, user__is_active = True)
			if account.Upload_Photo:
				pic_url =  '/media/'+str(account.Upload_Photo)+'/'
			else:
				pic_url =  '/media/employes/sss-logo.png/'

			return {'name':account.Name,'designation':account.Designation, 'profilepic_url':pic_url}
		except Account.DoesNotExist:
			return {'name':'Developer', 'designation':'Developer', 'profilepic_url':'/media/employes/sss-logo.png/'}
	else:
		return {'designation':'Unknown', 'profilepic_url':'/media/employes/sss-logo.png/'}

def vendor_updateledger(request, cat, fnc, pdata, inst):
	if fnc == 'create':
		if cat == 'vendinv':
			create = Vendor_Ledger.objects.create(
				Date = dt.date(),
				Related_Project = pdata['pj'], 
				Ref_No = inst.Invoice_No,
				Partner = inst.PO_No.Vendor.Supplier_Name,
				Credit = inst.Invoice_Amount,
				Order_No = inst.PO_No.PO_No,
				Lock_Status = 1,
				Row_ID = inst.id)
		else:
			create = Vendor_Ledger.objects.create(
				Date = inst.Payment_Date.date(),
				Related_Project = pdata['pj'], 
				Ref_No = inst.id,
				Partner = inst.PO_No.Vendor.Supplier_Name,
				Debit = inst.Paid_Amount,
				Order_No = inst.PO_No.PO_No,
				Lock_Status = 1,
				Row_ID = inst.id)
	elif fnc == 'edit':
		if cat == 'vendinv':
			updt = Vendor_Ledger.objects.filter(Row_ID=inst.id)
			update = updt.update(
				Date = dt.date(),
				Related_Project = pdata['pj'], 
				Ref_No = inst.Invoice_No,
				Partner = inst.PO_No.Vendor.Supplier_Name,
				Credit = inst.Invoice_Amount,
				Order_No = inst.PO_No.PO_No,
				Lock_Status = 1,
				Row_ID = inst.id)
		else:
			updt = Vendor_Ledger.objects.filter(Row_ID=inst.id)
			update = updt.update(
				Date = inst.Payment_Date.date(),
				Related_Project = pdata['pj'], 
				Ref_No = inst.id,
				Partner = inst.PO_No.Vendor.Supplier_Name,
				Debit = inst.Paid_Amount,
				Order_No = inst.PO_No.PO_No,
				Lock_Status = 1,
				Row_ID = inst.id)
	else:
		if cat == 'vendinv':
			updt = Vendor_Ledger.objects.filter(Row_ID=inst.id)
			updt.delete()
		else:
			updt = Vendor_Ledger.objects.filter(Row_ID=inst.id)
			updt.delete()


def customer_updateledger(request, cat, fnc, pdata, inst):
	if fnc == 'edit':
		updt = Customer_Ledger.objects.filter(Row_ID=inst.id, Debit__isnull=False).last() if cat == 'custinv' else Customer_Ledger.objects.filter(Row_ID=inst.id, Credit__isnull=False).last()
		updt.delete()
		
	if fnc == 'create' or fnc == 'edit': 
		lgr_0 = Customer_Ledger.objects.filter(Lock_Status=1).order_by('Date', 'Sr_No').last()
		if cat == 'custinv':
			lgr_cust = Customer_Ledger.objects.filter(Lock_Status=1, Partner = inst.Order.Customer_Name.Customer_Name).order_by('Date', 'Sr_No').last()
		else:
			lgr_cust = Customer_Ledger.objects.filter(Lock_Status=1, Partner = inst.Order_No.Customer_Name.Customer_Name).order_by('Date', 'Sr_No').last()			
		
		bal = lgr_0.Bal_All if lgr_0 != None else 0
		bal_cust = lgr_cust.Bal_Customer if lgr_cust != None else 0
		srno = lgr_0.Sr_No if lgr_0 != None else 0
		dt = inst.Invoice_Date if cat == 'custinv' else inst.Payment_Date
		
		if cat == 'custinv':		
			create = Customer_Ledger.objects.create(
				Date = inst.Invoice_Date,
				Related_Project = pdata['pj'], 
				Ref_No = inst.Invoice_No,
				Partner = inst.Order.Customer_Name.Customer_Name,
				Debit = inst.Invoice_Amount,
				Lock_Status = 1,
				Row_ID = inst.id)
		else:
			create = Customer_Ledger.objects.create(
				Date = inst.Payment_Date,
				Related_Project = pdata['pj'], 
				Ref_No = inst.id,
				Partner = inst.Order_No.Customer_Name.Customer_Name,
				Credit = inst.Received_Amount,
				Lock_Status = 1,
				Row_ID = inst.id)

	else:
		if cat == 'custinv':
			updt = Customer_Ledger.objects.filter(Row_ID=inst.id, Debit__isnull=False).last()
			srno_del = updt.Sr_No
			updt.delete()
		else:
			updt = Customer_Ledger.objects.filter(Row_ID=inst.id, Credit__isnull=False).last()
			srno_del = updt.Sr_No
			updt.delete()


	if fnc == 'create' or fnc == 'edit':
		if lgr_0 == None or (dt.date() >= lgr_0.Date):
			lgr_1 = Customer_Ledger.objects.filter(Row_ID=inst.id, Debit__isnull=False).last() if cat == 'custinv' else Customer_Ledger.objects.filter(Row_ID=inst.id, Credit__isnull=False).last()
			lgr_1.Sr_No = srno + 1
			lgr_1.Bal_All = float(bal) + inst.Invoice_Amount if cat == 'custinv' else float(bal) - inst.Received_Amount
			lgr_1.save()
		else:
			lg_last = Customer_Ledger.objects.filter(Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg = Customer_Ledger.objects.filter(Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')
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
			lgr_cust1 = Customer_Ledger.objects.filter(Row_ID=inst.id, Debit__isnull=False).last() if cat == 'custinv' else Customer_Ledger.objects.filter(Row_ID=inst.id, Credit__isnull=False).last()
			lgr_cust1.Bal_Customer = float(bal_cust) + inst.Invoice_Amount if cat == 'custinv' else float(bal_cust) - inst.Received_Amount
			lgr_cust1.save()
		
		else:

			if cat == 'custinv':
				lg_cust_last = Customer_Ledger.objects.filter(Partner = inst.Order.Customer_Name.Customer_Name).filter(Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
				lg_cust = Customer_Ledger.objects.filter(Partner = inst.Order.Customer_Name.Customer_Name).filter(Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')
			else:
				lg_cust_last = Customer_Ledger.objects.filter(Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Date__lt=dt, Lock_Status=1).order_by('Date', 'Sr_No').last()
				lg_cust = Customer_Ledger.objects.filter(Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Date__gte=dt, Lock_Status=1).order_by('Date', 'Sr_No')

			bal_cust = lg_cust_last.Bal_Customer if lg_cust_last != None else 0
			for k in lg_cust:
				print(k.Ref_No)
				if k.Debit != None:
					bal_cust = bal_cust + k.Debit
				else:
					if k.Credit:
						bal_cust = bal_cust - k.Credit
				k.Bal_Customer = bal_cust
				print(k.Bal_Customer)
				k.save()
	else:
		lg_last = Customer_Ledger.objects.filter(Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
		lg = Customer_Ledger.objects.filter(Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')
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
			lg_cust_last = Customer_Ledger.objects.filter(Partner = inst.Order.Customer_Name.Customer_Name).filter(Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg_cust = Customer_Ledger.objects.filter(Partner = inst.Order.Customer_Name.Customer_Name).filter(Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')
		else:
			lg_cust_last = Customer_Ledger.objects.filter(Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Sr_No__lt=srno_del, Lock_Status=1).order_by('Date', 'Sr_No').last()
			lg_cust = Customer_Ledger.objects.filter(Partner = inst.Order_No.Customer_Name.Customer_Name).filter(Sr_No__gte=srno_del, Lock_Status=1).order_by('Date', 'Sr_No')

		bal_cust = lg_cust_last.Bal_Customer if lg_cust_last != None else 0
		
		for k in lg_cust:
			if k.Debit != None:
				bal_cust = bal_cust + k.Debit
			else:
				if k.Credit:
					bal_cust = bal_cust - k.Credit
			k.Bal_Customer = bal_cust
			k.save()





		
