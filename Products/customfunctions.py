from datetime import date, datetime, timedelta 
from django.db.models import Sum, Avg, Count
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

def assign_paystatus_to_po(request, pay_id, fnc):
  
  payment = Vendor_Payment_Status.objects.get(id=pay_id)
  payment.user = Account.objects.get(user=request.user)
  payment.save()
  
  if not payment.PO_No:
  	po_no = payment.Invoice_No.PO_No
  	payment.PO_No = po_no
  	payment.save()
  else:
  	if payment.Invoice_No:
	  	inv = Vendor_Invoices.objects.filter(Invoice_No=payment.Invoice_No.Invoice_No).last()
	  	inv.Payment_Status = payment
	  	inv.save()
	  	payment = Vendor_Payment_Status.objects.get(id=pay_id)
	  	inv_paid = sum(Vendor_Payment_Status.objects.filter(Invoice_No=payment.Invoice_No).values_list('Paid_Amount', flat=True))
  		if inv.Due_Amount <= inv_paid:
	  		inv.Due_Amount = 0
	  		inv.Payment_Cleared_Date = payment.Payment_Date
	  		inv.save()
	  	else:
	  		inv.Due_Amount = inv.Due_Amount - inv_paid
	  		inv.Payment_Cleared_Date = None
	  		inv.save()
  
  po = Purchases.objects.get(PO_No=payment.PO_No.PO_No)
  po.Payment_Status = payment
  po.save()

  payment = Vendor_Payment_Status.objects.get(id=pay_id)
  vendor = payment.PO_No.Vendor

  invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor).order_by('Invoice_Date')
  pays = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor).order_by('Payment_Date')
  
  invs_amnt = sum(invs.values_list('Invoice_Amount', flat=True))
  invs_due = sum(invs.values_list('Due_Amount', flat=True))
  pays_total = sum(pays.values_list('Paid_Amount', flat=True))

  due = invs_amnt - pays_total
  case1 = Vendor_Invoices.objects.filter(PO_No=payment.PO_No, Due_Amount__gt=0).order_by('Invoice_Date')
  case2 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor, Due_Amount__gt=0).order_by('Invoice_Date')

  case3 = Vendor_Invoices.objects.filter(PO_No=payment.PO_No, Due_Amount=0).order_by('Invoice_Date')
  case4 = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor, Due_Amount=0).order_by('Invoice_Date')

  if due > 0:
  	if due != invs_due:
  		diff = invs_due - due 
	  	if diff > 0: # if it is positive diff  deduct from other invoices i.e decrease due amount
	  		diff = inv_adj(request, case1, diff, pay_id)
	  		if diff > 0:
	  			diff = inv_adj(request, case2, diff, pay_id)
		  	# if still duff > 0, its remains as advance
	  	elif diff < 0: # increase due amount
	  		diff = -(diff)
	  		diff = inv_adj1(request, case1, diff)
	  		if diff > 0:
	  			diff = inv_adj1(request, case2, diff)
	  			if diff > 0:
	  				diff = inv_adj1(request, case3, diff)
	  				if diff > 0:
	  					diff = inv_adj1(request, case4, diff)
  elif due == 0:
  	pass
  else:
  	Vendor_Invoices.objects.filter(PO_No__Vendor=vendor, Due_Amount__gt=0).update(Due_Amount=0, Payment_Cleared_Date=payment.Payment_Date, Payment_Status=payment)


def paymentdelete(request, poid, invid, dlt_amount):
	po = Purchases.objects.get(id=poid)
	inv =  Vendor_Invoices.objects.filter(id=invid).last()

	inv_paid = inv.Invoice_Amount - inv.Due_Amount
	
	if dlt_amount >= inv_paid:
		dlt_amount = dlt_amount - inv_paid
		inv.Due_Amount = inv.Invoice_Amount
		inv.Payment_Cleared_Date = None
		inv.Payment_Status = None
		inv.save()
	else:
		inv.Due_Amount = inv.Invoice_Amount - (inv_paid - dlt_amount)
		inv.Payment_Cleared_Date = None
		inv.save()
		dlt_amount = 0
	
	if dlt_amount > 0:
		case1 = Vendor_Invoices.objects.filter(PO_No=po, Due_Amount__gt=0).order_by('Invoice_Date')
		case2 = Vendor_Invoices.objects.filter(PO_No__Vendor=po.Vendor, Due_Amount__gt=0).order_by('Invoice_Date')
		case3 = Vendor_Invoices.objects.filter(PO_No=po, Due_Amount=0).order_by('Invoice_Date')
		case4 = Vendor_Invoices.objects.filter(PO_No__Vendor=po.Vendor, Due_Amount=0).order_by('Invoice_Date')

		diff = dlt_amount

		diff = inv_adj1(request, case1, diff)
		if diff > 0:
			diff = inv_adj1(request, case2, diff)
			if diff > 0:
				diff = inv_adj1(request, case3, diff)
				if diff > 0:
					diff = inv_adj1(request, case4, diff)

	pay = Vendor_Payment_Status.objects.filter(PO_No=po).last()
	if pay:			
		assign_paystatus_to_po(request, pay.id)
	else:
		pay = Vendor_Payment_Status.objects.filter(PO_No__Vendor=po.Vendor).last()
		if pay:			
			assign_paystatus_to_po(request, pay.id)


def inv_adj(request, invs, diff, pay_id):
	if invs != None:
		payment = Vendor_Payment_Status.objects.get(id=pay_id)
		for x in invs:
			if x.Due_Amount <= diff:
				diff = diff - x.Due_Amount
				x.Due_Amount = 0
				x.Payment_Status = payment
				x.Payment_Cleared_Date = payment.Payment_Date
				x.save()
			else:
				x.Due_Amount = x.Due_Amount - diff
				x.Payment_Cleared_Date = None
				x.save()
				diff = 0
	return diff

def inv_adj1(request, invs, diff):
	if invs != None:
		for x in invs:
			if diff >= (x.Invoice_Amount - x.Due_Amount):
				diff = diff - (x.Invoice_Amount - x.Due_Amount)
				x.Due_Amount = x.Invoice_Amount
				x.Payment_Status = None
				x.Payment_Cleared_Date = None
				x.save()
			else:
				x.Due_Amount = x.Due_Amount + diff
				x.Payment_Cleared_Date = None
				x.save()
				diff = 0
	return diff



def adjust_payments_to_invoices(request, poid, invid):
	po = Purchases.objects.get(id=poid)
	vendor = po.Vendor
	inv = Vendor_Invoices.objects.filter(id=invid).last()
	inv.Due_Amount = inv.Invoice_Amount
	inv.save()
	inv = Vendor_Invoices.objects.filter(id=invid).last()

	if Vendor_Payment_Status.objects.filter(Invoice_No=inv):
		assign_paystatus_to_po(request, Vendor_Payment_Status.objects.filter(Invoice_No=inv.Invoice_No).id, 'edit')
	else:
		case1 = Vendor_Payment_Status.objects.filter(PO_No=po).order_by('Payment_Date')
		case2 = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor).order_by('Payment_Date')
		# case3 = Vendor_Invoices.objects.filter(PO_No=po).order_by('Invoice_Date')
		# case4 =Vendor_Invoices.filter(PO_No__Vendor=po.Vendor).order_by('Invoice_Date')

		if case1 == None and case2 == None:
			pass
		else:
			if case1:
				assign_paystatus_to_po(request, case1.last().id, 'edit')
			else:
				if case2:
					assign_paystatus_to_po(request, case2.last().id, 'edit')

		# 	if case1:
		# 		tpay = sum(case1.values_list('Paid_Amount', flat=True))
		# 		tinv = sum(case3.values_list('Invoice_Amount', flat=True))

		# 		if tpay > tinv:
		# 			diff = tpay - tinv
		# 			if diff >= inv.Due_Amount:
		# 				diff = diff - inv.Due_Amount
		# 				inv.Due_Amount = 0
		# 				inv.Payment_Status = case1.last()
		# 				inv.Payment_Cleared_Date = case1.last().Payment_Date
		# 				inv.save()
		# 				case11 = Vendor_Invoices.objects.filter(PO_No=po, Due_Amount__gt=0).order_by('Invoice_Date')
		# 				case22 = Vendor_Invoices.objects.filter(PO_No__Vendor=po.Vendor, Due_Amount__gt=0).order_by('Invoice_Date')
		# 				en = 1
		# 				if case11:
		# 					inv_adj(request, case11, diff, case1.last().id)
		# 					if diff > 0:
		# 						inv_adj(request, case22, diff, case1.last().id)
		# 						en = 0
		# 				elif case22 and en == 1:
		# 					inv_adj(request, case22, diff, case1.last().id)
		# 				else:
		# 					pass
		# 			else:
		# 				inv.Due_Amount = inv.Due_Amount - diff
		# 				inv.Payment_Cleared_Date = None
		# 				inv.save()
		# 		elif tpay < tinv:
		# 			pass
		# 		else:
		# 			pass
		# if case2:
		# 		tpay = sum(case2.values_list('Paid_Amount', flat=True))
		# 		tinv = sum(case4.values_list('Invoice_Amount', flat=True))

		# 		if tpay > tinv:
		# 			diff = tpay - tinv
		# 			if diff >= inv.Due_Amount:
		# 				diff = diff - inv.Due_Amount
		# 				inv.Due_Amount = 0
		# 				inv.Payment_Status = case1.last()
		# 				inv.Payment_Cleared_Date = case1.last().Payment_Date
		# 				inv.save()
		# 				case11 = Vendor_Invoices.objects.filter(PO_No=po, Due_Amount__gt=0).order_by('Invoice_Date')
		# 				case22 = Vendor_Invoices.objects.filter(PO_No__Vendor=po.Vendor, Due_Amount__gt=0).order_by('Invoice_Date')
		# 				if case11:
		# 					inv_adj(request, case11, diff, case1.last().id)
		# 				elif case22:
		# 					inv_adj(request, case22, diff, case1.last().id)
		# 				else:
		# 					pass
		# 			else:
		# 				inv.Due_Amount = inv.Due_Amount - diff
		# 				inv.Payment_Cleared_Date = None
		# 				inv.save()
		# 		elif tpay < tinv:
		# 			pass
		# 		else:
		# 			pass

def adj_pay_to_all_inv(request, vendor):
	x = 0
	# invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor, Due_Amount = 0).order_by('Invoice_Date')
	# invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor).order_by('Invoice_Date')
	

	# pays = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor).order_by('Payment_Date')
	# # invs_total = sum(invs.values_list('Invoice_Amount', flat=True))
	# pays_total = sum(pays.values_list('Paid_Amount', flat=True))

	# invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor).order_by('Invoice_Date')
	# for x in invs:
	# 	if pays_total >= x.Invoice_Amount:
	# 		pays_total = pays_total - x.Invoice_Amount
	# 		x.Due_Amount = 0
	# 		x.Payment_Cleared_Date = pays.last().Payment_Date
	# 		# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 		x.Payment_Status = pays.last()
	# 		x.save()
	# 	else:
	# 		if pays_total > 0:
	# 			x.Due_Amount = x.Invoice_Amount - pays_total
	# 			x.Payment_Status = pays.last()
	# 			# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 			pays_total = 0
	# 			x.save()
	# 		else:
	# 			x.Due_Amount = x.Invoice_Amount
	# 			x.save()




	# diff = invs_total - pays_total
	# invs_due = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor, Due_Amount__gt=0).order_by('Invoice_Date')
	# if invs_due:
	# 	for x in invs_due:
	# 		if diff >= x.Invoice_Amount:
	# 			diff = diff - x.Invoice_Amount
	# 			x.Due_Amount = 0
	# 			x.Payment_Cleared_Date = pays.last().Payment_Date
	# 			# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 			x.Payment_Status = pays.last()
	# 			x.save()
	# 		else:
	# 			if diff > 0:
	# 				x.Due_Amount = x.Invoice_Amount - diff
	# 				x.Payment_Status = pays.last()
	# 				# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 				diff = 0
	# 				x.save()
	# 			else:
	# 				x.Due_Amount = x.Invoice_Amount

	# if invs_total < pays_total:
	# 	diff = pays_total - invs_total
	# 	invs_due = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor, Due_Amount__gt=0).order_by('Invoice_Date')
	# 	if invs_due:
	# 		for x in invs_due:
	# 			if diff >= x.Invoice_Amount:
	# 				diff = diff - x.Invoice_Amount
	# 				x.Due_Amount = 0
	# 				x.Payment_Cleared_Date = pays.last().Payment_Date
	# 				# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 				x.Payment_Status = pays.last()
	# 				x.save()
	# 			else:
	# 				if diff > 0:
	# 					x.Due_Amount = x.Invoice_Amount - diff
	# 					x.Payment_Status = pays.last()
	# 					# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 					diff = 0
	# 					x.save()
	# 				else:
	# 					x.Due_Amount = x.Invoice_Amount

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
			PO_Date=date.today(), PO_Value=vdi.Invoice_Amount, GST_Amount=vdi.GST_Amount, Lock_Status=1, Is_Billed=1, Is_No_PO=1, FY=get_financial_year(str(date.today())))

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

