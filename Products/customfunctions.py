from datetime import date, datetime, timedelta 
from django.db.models import Sum, Avg, Count, F
from.models import *
from django.http import HttpResponse, JsonResponse
from Projects.fyear import get_financial_year, get_fy_date

def genPO_initial_dataload(request, poid, last_poid):
	fd = Purchases.objects.get(id=poid)
	fd.PO_From = CompanyDetails.objects.all().last() or None
	fd.Shipping_To = CompanyDetails.objects.all().last() or None
	fd.Vendor_Contact = VendContDt.objects.filter(Supplier_Name=fd.Vendor).last() or None
	fd.FY = get_financial_year(str(date.today()))

	########### PO Number Update ##############
	last_po = Purchases.objects.get(id=last_poid) if last_poid != None else None
	if last_po != None:		
		if fd.FY == last_po.FY:
			fd.PO_No_1 = last_po.PO_No_1 + 1
		else:
			fd.PO_No_1 = 1
	else: 
		fd.PO_No_1 = 1 
	 
	if len(str(fd.PO_No_1)) == 1:  
		pono1 = '00'+str(fd.PO_No_1)
	elif len(str(fd.PO_No_1)) == 2:
		pono1 = '0'+str(fd.PO_No_1)
	else:
		pono1 = fd.PO_No_1
	
	fd.PO_No_Format = No_Formats.objects.filter(No_Format_Related_To='PO').last()
	fd.PO_No = str(fd.PO_No_Format.No_Format)+str(fd.FY)+'/'+str(pono1)
	###########End###########

	############# General Terms and Conditions #############
	tc = Purchase_TC.objects.all().last()
	if tc:
		po_tc = PO_Terms_Conditions.objects.create(PO_No=fd, Terms_and_Condition1=tc.Terms_and_Condition1 or None, Terms_and_Condition2=tc.Terms_and_Condition2 or None,
		Terms_and_Condition3=tc.Terms_and_Condition3 or None, Terms_and_Condition4=tc.Terms_and_Condition4 or None, 
		Terms_and_Condition5=tc.Terms_and_Condition5 or None, Terms_and_Condition6=tc.Terms_and_Condition6 or None,
		Terms_and_Condition7=tc.Terms_and_Condition7 or None, Terms_and_Condition8=tc.Terms_and_Condition8 or None)	
	else:
		po_tc = PO_Terms_Conditions.objects.create(PO_No=fd)

	fd.Terms_and_Conditions = po_tc

	###########End###########
	
	fd.Packing_and_Forwarding = 'Inclusive'
	fd.user = Account.objects.get(user=request.user)
	fd.PO_Value = 0
	fd.Payment_Term_1 = '50% Advance'
	fd.Payment_Term_2 = 'Balance Against Delivery'
	fd.Warranty = 1
	fd.Warranty_In = 'Year'
	fd.save()

def update_po_amount(request, poid):
	po = Purchases.objects.get(id=poid)
	items = Copy_PO_Items.objects.filter(PO_No=po)
	if not items:
		return 0

	po_value = 0
	for x in items:
		po_value = po_value + (x.Unit_Price*x.Quantity) + (x.Unit_Price*x.Quantity*x.GST/100)
	po.PO_Value = po_value
	if po.Due_Amount == None:
		po.Due_Amount = po_value
	po.save()

def update_qt_amount(request, qid):
	qt = Quotes.objects.get(id=qid)
	items = Copy_Quote_Items.objects.filter(Quote_No=qt)
	if not items:
		return 0

	qt_value = 0
	for x in items:
		qt_value = qt_value + (x.Unit_Price*x.Quantity)
	qt.Quote_Value = qt_value

	qt.save()

def inv_due_agnst_pay(request, mode, pay_id):
	print('no')
	payment = Vendor_Payment_Status.objects.get(id=pay_id)
	payment.user = Account.objects.get(user=request.user)
	payment.save()

	if payment.Invoice_No:
		inv = Vendor_Invoices.objects.filter(Invoice_No=payment.Invoice_No.Invoice_No).last()
		if mode == 'edit':
			inv.Due_Amount = inv.Invoice_Amount
			inv.save()
			inv = Vendor_Invoices.objects.filter(Invoice_No=payment.Invoice_No.Invoice_No).last()

		adjf = inv.Due_Amount - payment.Paid_Amount
		dp, dn = 0, 0
		print('adjf', adjf)
		if adjf < 0:
			dn = -(adjf)
			if dn < 1 and dn >= 0:
				inv.Roundoff = dn
				inv.save()
				dn = 0
		elif adjf > 0:
			dp = adjf
			if dp < 1 and dp >= 0:
				inv.Roundoff = dp
				inv.save()
				dp = 0
		else:
			pass
		
		if dp == 0 and dn == 0:
			inv.Due_Amount = 0
			inv.Payment_Cleared_Date = payment.Payment_Date
			inv.Payment_Status = payment
			inv.Final_Payment_Status = 1
			inv.save()
			po = Purchases.objects.filter(PO_No=payment.PO_No.PO_No).last()
			po.Payment_Status = payment
			po.save()
			print('create 1')
			return 1
		elif dp > 0:
			inv.Due_Amount = inv.Due_Amount - payment.Paid_Amount
			inv.Payment_Cleared_Date = None
			inv.Final_Payment_Status = 0
			inv.save()
			po = Purchases.objects.filter(PO_No=payment.PO_No.PO_No).last()
			po.Payment_Status = payment
			po.save()
			print('2')
		elif dn > 0:
			inv.Due_Amount = 0
			inv.Payment_Cleared_Date = payment.Payment_Date
			inv.Payment_Status = payment
			inv.Final_Payment_Status = 1
			inv.save()
			po = Purchases.objects.filter(PO_No=payment.PO_No.PO_No).last()
			po.Payment_Status = payment
			po.save()
			if mode == 'create':
				adj_invs_dues_p(request, payment, dn)
				print('ex')
		else:
			pass

		if mode == 'edit':
			print('edit')
			balance_inv_dues(request, payment.PO_No.Related_Project, payment.PO_No.Vendor, payment, inv.id)

def adj_invs_dues_p(request, payment, diff):
  vendor = payment.PO_No.Vendor
  proj = payment.PO_No.Related_Project
  

  case1 = Vendor_Invoices.objects.filter(PO_No=payment.PO_No, Due_Amount__gt=0, PO_No__Related_Project=proj).order_by('Invoice_Date')
  case2 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount__gt=0, PO_No__Related_Project=proj).order_by('Invoice_Date')
  
  diff = inv_adj(request, case1, diff, payment.id)
  if diff > 0:
  	diff = inv_adj(request, case2, diff, payment.id)
  
  case2.filter(Due_Amount__gt=0, Due_Amount__lt=1).update(Due_Amount=0, Roundoff=F('Due_Amount'))

def inv_adj(request, invs, diff, pay_id):
	if invs != None:
		payment = Vendor_Payment_Status.objects.get(id=pay_id)
		for x in invs:
			if x.Due_Amount <= diff:
				diff = diff - x.Due_Amount
				x.Due_Amount = 0
				x.Payment_Status = payment
				x.Payment_Cleared_Date = payment.Payment_Date
				x.Final_Payment_Status = 1
				x.Roundoff = 0
				x.save()
			else:
				x.Due_Amount = x.Due_Amount - diff
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.Roundoff = 0
				x.save()
				diff = 0
	return diff

def balance_inv_dues(request, proj, vendor, payment, exclude):
	invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  PO_No__Vendor__Address_Type='Billing', PO_No__Related_Project=proj).order_by('Invoice_Date')
	pays = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor, PO_No__Related_Project=proj).order_by('Payment_Date')
  
	invs_amnt = sum(invs.values_list('Invoice_Amount', flat=True))
	invs_due = sum(invs.values_list('Due_Amount', flat=True)) +  sum(invs.values_list('Roundoff', flat=True))
	pays_total = sum(pays.values_list('Paid_Amount', flat=True))

	print(invs_due, invs_amnt - pays_total)

	if (invs_amnt == pays_total) or (invs_amnt < pays_total):
		Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount__gt=0, PO_No__Related_Project=proj).update(Due_Amount=0, Payment_Cleared_Date=payment.Payment_Date, Payment_Status=payment)
		print('all due set 0')
		return 3

	if invs_due == (invs_amnt - pays_total): 
		print('all matched')
		return 4
	elif (invs_amnt - pays_total) > invs_due:
		diff = (invs_amnt - pays_total) - invs_due #it should be decrease from invs
		adj_invs_dues_n(request, payment, diff, exclude)
		print(diff, '5')
	else:
		diff = invs_due - (invs_amnt - pays_total)
		adj_invs_dues_p(request, payment, diff)
		print('6')

	Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount__gt=0, PO_No__Related_Project=proj, Due_Amount__lt=1).update(Due_Amount=0, Roundoff=F('Due_Amount'))


def adj_invs_dues_n(request, payment, diff, excludeid):
  vendor = payment.PO_No.Vendor
  proj = payment.PO_No.Related_Project
  
  case1 = Vendor_Invoices.objects.filter(PO_No=payment.PO_No, Due_Amount__gt=0, PO_No__Related_Project=proj).exclude(id=excludeid).order_by('Invoice_Date')
  case2 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount__gt=0, PO_No__Related_Project=proj).exclude(id=excludeid).order_by('Invoice_Date')

  case3 = Vendor_Invoices.objects.filter(PO_No=payment.PO_No, Due_Amount=0, PO_No__Related_Project=proj).order_by('Invoice_Date')
  case4 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount=0, PO_No__Related_Project=proj).order_by('Invoice_Date')

  diff = inv_adj1(request, case1, diff)
  if diff > 0:
  	diff = inv_adj1(request, case2, diff)
  	if diff > 0:
  		diff = inv_adj1(request, case3, diff)
  		if diff > 0:
  			diff = inv_adj1(request, case4, diff)

def paymentdelete(request, ordid, invid, dlt_amount):
	order = Purchases.objects.get(id=ordid)
	inv =  Vendor_Invoices.objects.filter(id=invid).last()
	proj = inv.PO_No.Related_Project
	inv_rec = inv.Invoice_Amount - inv.Due_Amount

	if dlt_amount >= inv_rec:
		dlt_amount = dlt_amount - inv_rec
		inv.Due_Amount = inv.Invoice_Amount
		inv.save()
		pm = Vendor_Payment_Status.objects.filter(Invoice_No=inv)
		if pm:
			am = sum(pm.values_list('Paid_Amount', flat=True))
			inv.Due_Amount = inv.Invoice_Amount - am
			if inv.Due_Amount < 0:
				inv.Due_Amount = 0
				inv.save()
				dlt_amount = dlt_amount + am
				print('dlt_amount',dlt_amount)
		else:
			inv.Payment_Cleared_Date = None
			inv.Final_Payment_Status = 0
			inv.Payment_Status = None
			inv.save()

	else:
		inv.Due_Amount = inv.Invoice_Amount - (inv_rec - dlt_amount)
		inv.Payment_Cleared_Date = None
		inv.Final_Payment_Status = 0
		inv.save()
		dlt_amount = 0
	
	if dlt_amount > 0:
		case1 = Vendor_Invoices.objects.filter(PO_No=order, Due_Amount__gt=0, PO_No__Related_Project=proj).exclude(id=inv.id).order_by('Invoice_Date')
		case2 = Vendor_Invoices.objects.filter(PO_No__Vendor=PO_No.Vendor,  Due_Amount__gt=0, PO_No__Related_Project=proj).exclude(id=inv.id).order_by('Invoice_Date')
		case3 = Vendor_Invoices.objects.filter(PO_No=order, Due_Amount=0, PO_No__Related_Project=proj).order_by('Invoice_Date')
		case4 = Vendor_Invoices.objects.filter(PO_No__Vendor=PO_No.Vendor,   Due_Amount=0, PO_No__Related_Project=proj).order_by('Invoice_Date')

		diff = dlt_amount
		diff = inv_adj1(request, case1, diff)
		if diff > 0:
			diff = inv_adj1(request, case2, diff)
			if diff > 0:
				diff = inv_adj1(request, case3, diff)
				if diff > 0:
					diff = inv_adj1(request, case4, diff)
	
	pay = Vendor_Payment_Status.objects.filter(PO_No=order).last()
	if pay:			
		inv_due_agnst_pay(request, 'edit', pay.id)
	else:
		pay = Vendor_Payment_Status.objects.filter(PO_No__Vendor=PO_No.Vendor, PO_No__Related_Project=proj).last()
		if pay:			
			inv_due_agnst_pay(request, 'edid', pay.id)

def inv_adj1(request, invs, diff):
	if invs != None:
		for x in invs:
			if diff >= (x.Invoice_Amount - x.Due_Amount):
				diff = diff - (x.Invoice_Amount - x.Due_Amount)
				x.Due_Amount = x.Invoice_Amount
				x.Payment_Status = None
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.Roundoff = 0
				x.save()
			else:
				x.Due_Amount = x.Due_Amount + diff
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.Roundoff = 0
				x.save()
				diff = 0
	return diff

def adjust_payments_to_invoices(request, ordid, invid):
	order = Purchases.objects.get(id=ordid)
	vendor = order.Vendor
	inv = Vendor_Invoices.objects.filter(id=invid).last()
	inv.Due_Amount = inv.Invoice_Amount
	inv.Roundoff = 0
	inv.save()
	proj = inv.PO_No.Related_Project
	

	pays = Vendor_Payment_Status.objects.filter(Invoice_No=inv)
	print('due', inv.Invoice_No, inv.Due_Amount)
	
	if pays:
		for x in pays:
			print(x.Paid_Amount)
			inv_due_agnst_pay(request, 'create', x.id)
	else:
		case0 = Vendor_Payment_Status.objects.filter(Invoice_No=inv).order_by('Payment_Date')
		case1 = Vendor_Payment_Status.objects.filter(PO_No=order).order_by('Payment_Date')
		case2 = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor, PO_No__Related_Project=proj).order_by('Payment_Date')

		if case1 == None and case2 == None and case0 == None:
			pass
		else:
			if case0:
				inv_due_agnst_pay(request, 'edit', case0.last().id)
			elif case1:
				inv_due_agnst_pay(request, 'edit', case1.last().id)
			else:
				if case2:
					inv_due_agnst_pay(request, 'edit', case2.last().id)

def adj_pay_to_all_inv(request, vendor):
	x = 0

def update_vendor_invoice(request, invid, poid):
	po = Purchases.objects.get(id=poid)
	inv = Vendor_Invoices.objects.get(id=invid)

	po.Billing_Status = inv
	po.Is_Billed = 1
	inv.user = Account.objects.get(user=request.user)
	inv.save()
	po.save()

def updateduedays(request, invid):
	inv = Vendor_Invoices.objects.filter(id=invid).last()
	inv.Payment_Due_Date = inv.Invoice_Date.date() + timedelta(days=inv.Credit_Days)
	inv.Payment_Over_Due_Days = (date.today() - inv.Payment_Due_Date).days
	if inv.Payment_Over_Due_Days < 0:
		inv.Payment_Over_Due_Days = 0
	inv.save()

def update_delivery_status(request, poid, did):
	po = Purchases.objects.filter(id=poid).last()
	dl = PO_Delivery_Status.objects.get(id=did)
	dl.PO_No = po
	dl.user = Account.objects.get(user=request.user)
	dl.save()
	po.Delivery_Update = dl
	po.save()

def check_no_po(request, invid, pdata):
	vdi = Vendor_Invoices.objects.get(id=invid)
	if vdi.Against == 'No PO':
		fd = Purchases.objects.create(Related_Project=pdata['pj'], Purchase_Details=vdi.Invoice_Description or None, Vendor=vdi.Vendor or None, 
			PO_Date=date.today(), PO_Value=vdi.Invoice_Amount, GST_Amount=vdi.GST_Amount,  Is_Billed=1, Is_No_PO=1, FY=get_financial_year(str(date.today())))

		last_poid = Purchases.objects.filter(Is_No_PO=1).order_by('-id')
		last_poid = last_poid[1] if len(last_poid) > 1 else None
		last_po = Purchases.objects.get(id=last_poid.id) if last_poid != None else None
		if last_po != None:		
			if fd.FY == last_po.FY:
				fd.PO_No_1 = last_po.PO_No_1 + 1
			else:
				fd.PO_No_1 = 1
		else:
			fd.PO_No_1 = 1 
		
		if len(str(fd.PO_No_1)) == 1: 
			pono1 = '00'+str(fd.PO_No_1)
		elif len(str(fd.PO_No_1)) == 2:
			pono1 = '0'+str(fd.PO_No_1)
		else:
			pono1 = fd.PO_No_1
		
		fd.PO_No = 'DummpyPO'+str(fd.FY)+'/'+str(pono1)
		fd.save()
		vdi.PO_No = fd
		vdi.save()

def balance_inv_dues1(request, vendor):
	invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  PO_No__Vendor__Address_Type='Billing').order_by('Invoice_Date')
	pays = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor).order_by('Payment_Date')

	payment = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor).last()

	if payment:
		invs_amnt = sum(invs.values_list('Invoice_Amount', flat=True))
		invs_due = sum(invs.values_list('Due_Amount', flat=True)) +  sum(invs.values_list('Roundoff', flat=True))
		pays_total = sum(pays.values_list('Paid_Amount', flat=True))

		print(invs_due, invs_amnt - pays_total)

		if (invs_amnt == pays_total) or (invs_amnt < pays_total):
			Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount__gt=0).update(Due_Amount=0, Payment_Cleared_Date=payment.Payment_Date, Payment_Status=payment)
			print('all due set 0')
			return 3

		if invs_due == (invs_amnt - pays_total):
			print('all matched')
			return 4
		elif (invs_amnt - pays_total) > invs_due:
			diff = (invs_amnt - pays_total) - invs_due #it should be decrease from invs
			adj_invs_dues_n1(request,  diff)
			print(diff, '5')
		else:
			diff = invs_due - (invs_amnt - pays_total)
			case1 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount__gt=0).order_by('Invoice_Date')
			diff = inv_adj(request, case1, diff, payment.id)
			print('6')

def adj_invs_dues_n1(request, diff):
  vendor = payment.PO_No.Vendor
  proj = payment.Order_No.Related_Project
  
  case1 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount__gt=0, PO_No__Related_Project=proj).order_by('Invoice_Date')
  case2 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor,  Due_Amount=0, PO_No__Related_Project=proj).order_by('Invoice_Date')

  diff = inv_adj1(request, case1, diff)
  if diff > 0:
  	diff = inv_adj1(request, case2, diff)