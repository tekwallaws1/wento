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

def assign_paystatus_to_po(request, pay_id, poid):
  po = Purchases.objects.get(id=poid)
  payment = Vendor_Payment_Status.objects.get(id=pay_id)
  po.Payment_Status = payment
  po.save()

  if not payment.PO_No:
    payment.PO_No = po

  inv = Vendor_Invoices.objects.filter(PO_No=po).order_by('Invoice_Date')
  payments  = Vendor_Payment_Status.objects.filter(PO_No=po).order_by('Payment_Date')
  t_inv = sum(inv.values_list('Invoice_Amount', flat=True))
  t_pay = sum(payments.values_list('Paid_Amount', flat=True))
  #here t_pay = total payment paid except current payment, bcz pay_status not assigned to po

  if t_inv==0 and t_pay==0:
    payment.Payment_Type = 'Advance'

  elif t_inv - t_pay > 0:
    payment.Payment_Type = 'Due'
  else:
    payment.Payment_Type = 'Advance'

  payment.user = Account.objects.get(user=request.user)
  payment.save()  

def adjust_payments_to_invoices(request, poid):
  # if invoice lock and if any payments under this po before invoice gen.
  # inv_current = Vendor_Invoices.objects.filter(id=invid).last()
  po = Purchases.objects.get(id=poid)
  inv = Vendor_Invoices.objects.filter(PO_No=po).order_by('Invoice_Date')
  payments  = Vendor_Payment_Status.objects.filter(PO_No=po).order_by('Payment_Date')
  t_inv = inv.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0 if inv != None else 0
  t_pay = payments.aggregate(sum=Sum('Paid_Amount')).get('sum') or 0 if payments != None else 0
  vendor = po.Vendor
  # CASE-1: No Prev Invoices, No Payments (only cureent gen invoice)
  if len(inv) == 1 and t_pay==0:
    for x in inv:
      x.Due_Amount = x.Invoice_Amount
      x.save()
    adj_pay_to_all_inv(request, vendor)
    return 1

  # CASE-2: Previous invoices available against that po but no payments gainst po
  if len(inv) > 1 and t_pay==0:
    for x in inv:
      x.Due_Amount = x.Invoice_Amount
      x.save()
    adj_pay_to_all_inv(request, vendor)
    return 2

  # CASE-3: Invoices Due Amount Adjustments Against po and Received Paymants
  if t_inv+10 <= t_pay or t_inv-10 <= t_pay:
    # if total billing value =< total received value update all bills due as 0
    Vendor_Invoices.objects.filter(PO_No=po).update(Due_Amount=0)
    adj_pay_to_all_inv(request, vendor)
    return 3
  else:
    for x in inv:
      if t_pay > x.Invoice_Amount:
        x.Due_Amount = 0
        x.save()
        t_pay = t_pay - x.Invoice_Amount
      else:
        # means whole received payment is less than one single invoice amount
        x.Due_Amount = x.Invoice_Amount - t_pay
        t_pay = 0
        x.save()
        # Breaking for and while loops
    adj_pay_to_all_inv(request, vendor)
    return 4

def adj_pay_to_all_inv(request, vendor):
	# invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor, Due_Amount = 0).order_by('Invoice_Date')
	# invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor).order_by('Invoice_Date')
	pays = Vendor_Payment_Status.objects.filter(PO_No__Vendor=vendor).order_by('Payment_Date')
	# invs_total = sum(invs.values_list('Invoice_Amount', flat=True))
	pays_total = sum(pays.values_list('Paid_Amount', flat=True))

	invs = Vendor_Invoices.objects.filter(PO_No__Vendor=vendor).order_by('Invoice_Date')
	for x in invs:
		if pays_total >= x.Invoice_Amount:
			pays_total = pays_total - x.Invoice_Amount
			x.Due_Amount = 0
			x.Payment_Cleared_Date = pays.last().Payment_Date
			# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
			x.Payment_Status = pays.last()
			x.save()
		else:
			if pays_total > 0:
				x.Due_Amount = x.Invoice_Amount - pays_total
				x.Payment_Status = pays.last()
				# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
				pays_total = 0
				x.save()
			else:
				x.Due_Amount = x.Invoice_Amount
				x.save()


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

