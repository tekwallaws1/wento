from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from datetime import date, datetime, timedelta 
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.generic import View 
from .filters import *
from django.shortcuts import get_object_or_404, render
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required 
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Sum, Avg, Count
from Projects.fyear import get_financial_year, get_fy_date, get_fy_date_fy
from Projects.basedata import projectname, vendor_updateledger
from .customfunctions import genPO_initial_dataload, update_po_amount, update_qt_amount, assign_paystatus_to_po, adjust_payments_to_invoices, update_vendor_invoice, updateduedays, update_delivery_status, check_no_po, adj_pay_to_all_inv, paymentdelete
from num2words import num2words
from django.urls import reverse 
 
 
@login_required
def Purchases_Dashboard(request, proj, dur):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	lookup1 = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}

	if dur == 'FY':
		pos = Purchases.objects.filter(**lookup, Lock_Status=1, PO_Date__date__lte=date.today(), PO_Date__date__gte=get_fy_date_fy(), ds=1).order_by('PO_Date')
		payments = Vendor_Payment_Status.objects.filter(**lookup1,  Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date_fy()).order_by('Payment_Date')
	elif dur == 'All':
		pos = Purchases.objects.filter(**lookup, Lock_Status=1, ds=1).order_by('PO_Date')
		payments = Vendor_Payment_Status.objects.filter(**lookup1).order_by('Payment_Date')		
	else:
		pos = Purchases.objects.filter(**lookup, Lock_Status=1, PO_Date__date__lte=date.today(), PO_Date__date__gte=date.today()-timedelta(days=int(dur)), ds=1).order_by('PO_Date')
		payments = Vendor_Payment_Status.objects.filter(**lookup1,  Payment_Date__date__lte=date.today(), Payment_Date__date__gte=date.today()-timedelta(days=int(dur))).order_by('Payment_Date')

	vendors_list, t_pos, t_billed, t_paid_pay, t_due_pay, t_unbilled = [], [], [], [], [], []
	po_val, po_date, vend_list, pay_val, pay_date, pay_vend = [], [], [], [], [], []
	toc, ioc, toc_30, tbc, cbc, tbc_30 = 0,0,0,0,0,0 #counts
	tov, iov, tov_30, tbv, cbv, tbv_30, tdp, tpp, tpp_30 = 0,0,0,0,0,0,0,0,0 #value

	# pos
	toc, tov = len(pos), (pos.aggregate(sum=Sum('PO_Value')).get('sum') or 0)
	f_30 = pos.filter(PO_Date__date__lte=date.today(), PO_Date__date__gte=date.today()-timedelta(days=30))
	toc_30, tov_30 = len(f_30), (f_30.aggregate(sum=Sum('PO_Value')).get('sum') or 0)
	ip = pos.filter(Final_Status=0)
	ioc, iov = len(ip), (ip.aggregate(sum=Sum('PO_Value')).get('sum') or 0)

	# billing
	invs = Vendor_Invoices.objects.filter(**lookup1)
	f_30 = invs.filter(Invoice_Date__date__lte=date.today(), Invoice_Date__date__gte=date.today()-timedelta(days=30))
	tbc, tbv = len(invs), (invs.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)
	tbc_30, tbv_30 = len(f_30), (f_30.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)
	cbc, cbv = len(invs.filter(Due_Amount=0)), (invs.filter(Due_Amount=0).aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)

	# payments_30 days
	tpp_30 = payments.filter(Payment_Date__date__lte=date.today(), Payment_Date__date__gte=date.today()-timedelta(days=30)).aggregate(sum=Sum('Paid_Amount')).get('sum') or 0

	for x in pos:
		vend_list.append(x.Vendor.Short_Name)
		po_val.append(int(x.PO_Value))
		po_date.append(str((x.PO_Date+timedelta(days=1)).strftime('%m-%d-%Y')))
	
	vendors_list = list(dict.fromkeys(vend_list))

	for x in payments:
		pay_vend.append(x.PO_No.Vendor.Short_Name)
		pay_val.append(int(x.Paid_Amount))
		lst = [str((x.Payment_Date+timedelta(days=1)).strftime('%m-%d-%Y')), int(x.Paid_Amount), int(x.Paid_Amount)]
		pay_date.append(lst)

	#total billings and payments **Customer Wise
	for x in vendors_list:
		ordr = pos.filter(Vendor__Short_Name=x)
		t_ord = ordr.aggregate(sum=Sum('PO_Value')).get('sum')
		t_pos.append(int(t_ord))

		billed, pay, due, unbilled = 0, 0, 0, 0
		for y in ordr:
			billed = billed + (Vendor_Invoices.objects.filter(PO_No=y).aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)
			pay = pay + (Vendor_Payment_Status.objects.filter(PO_No=y).aggregate(sum=Sum('Paid_Amount')).get('sum') or 0)
		due = billed - pay
		unbilled = t_ord - billed

		# due = 0 if due < 0 else due
		unbilled = 0 if unbilled < 0 else unbilled

		t_billed.append(int(billed))
		t_paid_pay.append(int(pay))
		t_due_pay.append(int(due))
		t_unbilled.append(int(unbilled))

	tpp = sum(pay_val) #total rec pay
	tdp = tbv - tpp #total due
	count = {'toc':toc, 'toc_30':toc_30, 'ioc':ioc, 'tbc':tbc, 'tbc_30':tbc_30, 'cbc':cbc}
	val = {'tov':tov, 'tov_30':tov_30, 'iov':iov, 'tbv':tbv, 'tbv_30':tbv_30, 'cbv':cbv, 'tpp':tpp, 'tpp_30':tpp_30, 'tdp':tdp}
		
	return render(request, 'products/PurchasesDashboard.html', {'pdata':pdata, 'vendors_list':vendors_list, 't_pos':t_pos,
		't_billed':t_billed, 't_paid_pay':t_paid_pay, 't_due_pay':t_due_pay, 't_unbilled':t_unbilled, 'po_date':po_date, 'po_val':po_val, 
		'vend_list':vend_list, 'dur':dur, 'pay_val':pay_val, 'pay_date':pay_date, 'pay_vend':pay_vend, 'count':count, 'val':val})



@login_required
def PO_List(request, proj, status):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	# lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	table = Purchases.objects.filter(**lookup).order_by('-PO_Date')
	table_fy = Purchases.objects.filter(**lookup, PO_Date__date__lte=date.today(), PO_Date__date__gte=get_fy_date()).order_by('-PO_Date')

	form_select_vendor = PurchasesForm()
	form_select_vendor.fields["Vendor"].queryset = VendDt.objects.filter(Address_Type='Billing')
	
	# initiall it will take financial year table_fy data **when no filter applies
	# if any filter apply ut should take noram table
	filter_data = PurchasesFilter(request.GET, queryset=table_fy)
	table_fy = filter_data.qs
	table_data = table_fy
	has_filter = any(field in request.GET for field in set(filter_data.get_fields()))
	
	if has_filter: #update filter data queyset
		filter_data = PurchasesFilter(request.GET, queryset=table)
		table = filter_data.qs
		table_data = table

	if status == 'Inprogress':
		table_data = table_data.filter(Final_Status=0, Lock_Status=1)
	elif status == 'Closed':
		table_data = table_data.filter(Final_Status=1, Lock_Status=1)
	elif status == 'Total':
		table_data = table_data.filter(Lock_Status=1)
	elif status == 'Incomplete':
		table_data = table_data.filter(Final_Status=0, Lock_Status=0)
	else:
		pass

	total, closed, inprogress, tc, cc, ic = 0,0,0,0,0,0
	total_billed, total_piad, total_bills_count, po_paid, po_billed, po_bills_count, delivery = 0, 0, 0, [], [], [], []
	for x in table_data:
		if x.Billing_Status:
			billed=0
			bills_count = 0
			bills = Vendor_Invoices.objects.filter(PO_No=x)
			for y in bills:
				billed = billed + y.Invoice_Amount
				bills_count = bills_count + 1
			po_billed.append(int(billed))
			po_bills_count.append(bills_count)			
		else:
			po_billed.append(0)
			po_bills_count.append(0)
		
		if x.Payment_Status:
			pays = Vendor_Payment_Status.objects.filter(PO_No=x)
			print(pays)
			paid=0
			for z in pays:
				paid = paid + z.Paid_Amount
			po_paid.append(int(paid))
		else:
			po_paid.append(0)

		if x.Delivery_Update:
			dlv = PO_Delivery_Status.objects.filter(PO_No=x).order_by('Delivery_Date')
			delivery.append(dlv)		
		else:
			delivery.append(None)

	for x in table_data:
		if x.Lock_Status == 1:
			total, tc = int(total + x.PO_Value), tc+1 
		if x.Lock_Status == 1 and x.Final_Status == 1:
			closed, cc = int(closed + x.PO_Value), cc+1
		if x.Lock_Status == 1 and x.Final_Status == 0:
			inprogress, ic = int(inprogress + x.PO_Value), ic+1	
	pos = {'total':total, 'closed':closed, 'inprogress':inprogress}
	count = {'tc':tc, 'cc':cc, 'ic':ic}

	pay_form = POPaymentsForm()
	lookup1 = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	pay_form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup1, Payment_Final_Status=0)


	tableset = zip(table_data, po_billed, po_paid, po_bills_count, delivery)
	return render(request, 'products/PurchasesList.html', {'tableset':tableset, 'table':table_data, 'filter_data':filter_data, 'pdata':pdata, 'status':status, 
		'pos':pos, 'count':count, 'form_select_vendor':form_select_vendor, 'pay_form':pay_form})

@login_required
def PO_Form(request, proj, fnc, poid):
	pdata = projectname(request, proj) 
	if fnc == 'edit' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(Purchases, id=poid)
			form = POForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				fd = Purchases.objects.get(id=p.id)
				fd.user = Account.objects.get(user=request.user)
				fd.save()
				messages.success(request, "Selected Purchase Details Has Been Updated")
				return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])
			else:
				return render(request, 'products/POForm.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(Purchases, id=poid)
			form = POForm(instance=getdata)
			return render(request, 'products/POForm.html', {'form': form, 'pdata':pdata})
	elif fnc == 'edit_manually':		
		if request.method == 'POST':
			form = ManualPurchasesForm1(request.POST, request.FILES, instance=get_object_or_404(Purchases, id=poid))
			if form.is_valid():
				p = form.save()
				messages.success(request, 'PO Details Has Been Updated Successfully')
				return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])
			else:
				return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])
		else:
			form = ManualPurchasesForm1(instance=get_object_or_404(Purchases, id=poid))
			return render(request, 'products/POForm.html', {'form': form, 'pdata':pdata})

@login_required
def PO_Delivery_Form(request, proj, fnc, poid, did):
  pdata = projectname(request, proj)
  if fnc == 'edit':
    if request.method ==  'POST':
      getdata = get_object_or_404(PO_Delivery_Status, id=did)
      form = PODeliveryForm1(request.POST, request.FILES, instance=getdata)
      if form.is_valid():
        p= form.save()
        update_delivery_status(request, poid, p.id)
        messages.success(request, "Selected Delivery Details Has Been Updated")
        return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])
      else:
        return render(request, 'products/PODeliveryForm.html', {'form': form, 'pdata':pdata})
    else:
      getdata = get_object_or_404(PO_Delivery_Status, id=did)
      form = PODeliveryForm1(instance=getdata)
      return render(request, 'products/PODeliveryForm.html', {'form': form, 'pdata':pdata})

  elif fnc == 'delete': #Delete
    getdata = get_object_or_404(PO_Delivery_Status, id=did)
    getdata.delete()
    po = Purchases.objects.get(id=poid)
    if not po.PO_Delivery_Status:
      po.PO_Delivery_Status = PO_Delivery_Status.objects.filter(PO_No=po).order_by('Delivery_Date').last()
      po.save()
    messages.success(request, "Selected Delivery Details Has Deleted")
    return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])

  if request.method ==  'POST': #Create
    form = PODeliveryForm(request.POST, request.FILES)
    if form.is_valid():
      p = form.save()
      update_delivery_status(request, poid, p.id)
      messages.success(request, "Delivery Details Has Been Added")
      return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])
    else:
      return render(request, 'products/PODeliveryForm.html', {'form': form, 'pdata':pdata})
  else:
      form = PODeliveryForm()
      return render(request, 'products/PODeliveryForm.html', {'form': form, 'pdata':pdata})

@login_required
def PO_Payments_Form(request, proj, poid):
	pdata = projectname(request, proj)
	po = Purchases.objects.get(id=poid)
	if request.method ==  'POST': #Create
		form = POPaymentsForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			p.PO_No = po
			p.save() 
			assign_paystatus_to_po(request, p.id, 'create')
			# adjust_payments_to_invoices(request, po.id)
			# adj_pay_to_all_inv(request, po.Vendor)
			vendor_vendor_updateledger(request, 'vendpay', 'create', pdata, Vendor_Payment_Status.objects.get(id=p.id))
			messages.success(request, "Payment Has Been Added")
			return redirect('/%s/vendorpaymentslist/Paid/vendflt/'%pdata['pj'])
		else:
			return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})
	else:
		form = POPaymentsForm()
		return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})

@login_required
def Vendor_Payments_Form(request, proj, fnc, payid):
  pdata = projectname(request, proj)
  lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
  lookup1 = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}
  
  if fnc == 'edit':
    if request.method ==  'POST':
      getdata = get_object_or_404(Vendor_Payment_Status, id=payid)
      form = VendorPaymentForm1(request.POST, request.FILES, instance=getdata)
      if form.is_valid():
        p = form.save(commit=False)
        p= form.save()
        po = Purchases.objects.get(id=p.PO_No.id)
        assign_paystatus_to_po(request, p.id, fnc)
        # adjust_payments_to_invoices(request, po.id)
        # adj_pay_to_all_inv(request, po.Vendor)
        vendor_updateledger(request, 'vendpay', 'edit', pdata, Vendor_Payment_Status.objects.get(id=p.id))
        messages.success(request, "Selected Payment Details Has Been Updated")
        return redirect('/%s/vendorpaymentslist/Paid/vendflt/'%pdata['pj'])
      else:
        return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})
    else:
      getdata = get_object_or_404(Vendor_Payment_Status, id=payid)
      form = VendorPaymentForm1(instance=getdata)
      return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})

  elif fnc == 'delete':
    vendor_updateledger(request, 'vendpay', 'delete', pdata, Vendor_Payment_Status.objects.get(id=payid))
    getdata = get_object_or_404(Vendor_Payment_Status, id=payid)
    po = getdata.PO_No
    inv = getdata.Invoice_No
    dlt_amount = getdata.Paid_Amount
    getdata.delete()

    po = Purchases.objects.get(id=po.id)
    ag_po = Vendor_Payment_Status.objects.filter(PO_No=po).order_by('-Payment_Date')
    ag_vend = Vendor_Payment_Status.objects.filter(PO_No__Vendor=po.Vendor).order_by('-Payment_Date')

    if ag_po == None and ag_vend == None:
    	messages.success(request, "Selected Payment Details Has Deleted")
    	return redirect('/%s/vendorpaymentslist/Paid/vendflt/'%pdata['pj'])
    else:
    	if ag_po:
    		last_pay = ag_po.last()
    	else:
    		last_pay = ag_vend.last()
    	po.Payment_Status = last_pay
    	po.save()
    	po = Purchases.objects.get(id=po.id)
    	paymentdelete(request, po.id, inv.id, dlt_amount)
    	messages.success(request, "Selected Payment Details Has Deleted")
    	return redirect('/%s/vendorpaymentslist/Paid/vendflt/'%pdata['pj'])

  if request.method ==  'POST': #Create
    form = VendorPaymentForm(request.POST, request.FILES)
    if form.is_valid():
      p = form.save(commit=False)
      if p.PO_No==None and p.Invoice_No==None:
        messages.error(request, "Either PO No or Invoice No Must Be Geiven to Record Payment")
        return redirect('/%s/vendorpaymentslist/Paid/vendflt/'%pdata['pj'])
      p= form.save()
      if not p.PO_No: # when paymentbthrough invoice number
        p.PO_No = p.Invoice_No.PO_No
        p.save()
        assign_paystatus_to_po(request, p.id, fnc)
      else:
        assign_paystatus_to_po(request, p.id, fnc)
      # po = Purchases.objects.get(id=p.PO_No.id)
      # adjust_payments_to_invoices(request, po.id)
      # adj_pay_to_all_inv(request, p.PO_No.Vendor)
      vendor_updateledger(request, 'vendpay', 'create', pdata, Vendor_Payment_Status.objects.get(id=p.id))
      messages.success(request, "Payment Has Been Added")
      return redirect('/%s/vendorpaymentslist/Paid/vendflt/'%pdata['pj'])
    else:
      return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})
  else:
    if fnc == 'copy':
      getdata = get_object_or_404(Vendor_Payment_Status, id=payid)
      form = VendorPaymentForm(instance=getdata)
      return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})
    else:
      form = VendorPaymentForm()
      form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0, Lock_Status=1)
      form.fields["Invoice_No"].queryset = Vendor_Invoices.objects.filter(**lookup1, Due_Amount__gt=0)
      return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})

@login_required
def Vendor_Invoice_Form(request, proj, fnc, poid, invid):
  pdata = projectname(request, proj)
  lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
  if fnc == 'edit':
    if request.method ==  'POST':
      getdata = get_object_or_404(Vendor_Invoices, id=invid)
      form = VendorInvoicesForm(request.POST, request.FILES, instance=getdata)
      if form.is_valid():
        p= form.save()
        updateduedays(request, p.id)
        po = Purchases.objects.get(id=p.PO_No.id)
        update_vendor_invoice(request, p.id, po.id)
        adjust_payments_to_invoices(request, po.id, p.id)
        vendor_updateledger(request, 'vendinv', 'edit', pdata, Vendor_Invoices.objects.get(id=p.id))
        messages.success(request, "Selected Invoice Details Has Been Updated")
        return redirect('/%s/vendorinvoiceslist/Issued/'%pdata['pj'])
      else:
        return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
    else:
      getdata = get_object_or_404(Vendor_Invoices, id=invid)
      form = VendorInvoicesForm1(instance=getdata)
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
  	
  elif fnc == 'delete': #Delete
    vendor_updateledger(request, 'vendinv', 'delete', pdata, Vendor_Invoices.objects.get(id=invid))
    getdata = get_object_or_404(Vendor_Invoices, id=invid)    
    poid = getdata.PO_No.id
    if getdata.Against == 'No PO':
    	Purchases.objects.get(id=poid).delete()
    	messages.success(request, "Selected Invoice Details Has Been Deleted")
    	return redirect('/%s/vendorinvoiceslist/Issued/'%pdata['pj'])

    getdata.delete()
    po = Purchases.objects.get(id=poid)
    inv = Vendor_Invoices.objects.filter(PO_No=po).order_by('Invoice_Date').last()
    if inv:
	    adjust_payments_to_invoices(request, poid, inv.id)
	    if not po.Billing_Status:
	      po.Billing_Status = inv
	      po.save()
    messages.success(request, "Selected Invoice Details Has Been Deleted")
    return redirect('/%s/vendorinvoiceslist/Issued/'%pdata['pj'])

  if request.method ==  'POST': #Create
    form = VendorInvoicesForm(request.POST, request.FILES)
    if form.is_valid():
      p= form.save()
      check_no_po(request, p.id, pdata)
      p = Vendor_Invoices.objects.get(id=p.id)
      updateduedays(request, p.id)
      update_vendor_invoice(request, p.id, p.PO_No.id)
      adjust_payments_to_invoices(request, p.PO_No.id, p.id)
      vendor_updateledger(request, 'vendinv', 'create', pdata, Vendor_Invoices.objects.get(id=p.id))
      messages.success(request, "Vendor Invoice Has Been Registered")
      return redirect('/%s/vendorinvoiceslist/Issued/'%pdata['pj'])
    else:
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
  else:
    if fnc == 'copy':
      getdata = get_object_or_404(Vendor_Invoices, id=invid)
      form = VendorInvoicesForm(instance=getdata)
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
    else:
      form = VendorInvoicesForm()
      form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0, Final_Status=0, Lock_Status=1)
      form.fields["Vendor"].queryset = VendDt.objects.filter(Address_Type='Billing')
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required
def Vendor_Invoices_List(request, proj, status):
	pdata = projectname(request, proj)
	
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	form = VendorInvoicesForm()
	form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0)
	
	lookup = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}
	
	# update invoices due dates
	invoiceslist = Vendor_Invoices.objects.filter(**lookup, Last_Update__lt=date.today(), Due_Amount__gt=0)
	if invoiceslist:
		for x in invoiceslist:			
			x.Last_Update = date.today()
			x.save()
			updateduedays(request, x.id)

	table_data = Vendor_Invoices.objects.filter(**lookup).order_by('-Invoice_Date')
	# table_fy_inv = Vendor_Invoices.objects.filter(**lookup, Invoice_Date__date__lte=date.today(), Invoice_Date__date__gte=get_fy_date()).order_by('-Invoice_Date')
	
	filter_data = VendorInvoicesFilter(request.GET, queryset=table_data)
	table_data = filter_data.qs
	
	# has_filter_inv = any(field in request.GET for field in set(filter_data.get_fields()))
	# if has_filter_inv: #update filter data queyset
	# 	filter_data = VendorInvoicesFilter(request.GET, queryset=table_inv)
	# 	table_inv = filter_data.qs
	# 	table_data = table_inv

	full_due_inv, part_due_inv, full_clear_inv, total_billing, total_paid = 0, 0, 0, 0, 0
	fdc, pdc, fcc, tbc = 0, 0, 0, 0 #count
	orders_list, invoices_list  = [], []

	pos_list = []
	
	for x in table_data:
		pos_list.append(x.PO_No)
	pos_list = list(dict.fromkeys(pos_list))

	for x in pos_list:
		inv = Vendor_Invoices.objects.filter(PO_No=x).order_by('Invoice_Date')
		pay = Vendor_Payment_Status.objects.filter(PO_No=x).order_by('Payment_Date')
		invoices_list.append(inv)
		inv_total 	 = sum(inv.values_list('Invoice_Amount', flat=True)) or 0
		
		total_billing = total_billing + inv_total
		tbc = tbc + len(inv)

		for a in inv:
			if a.Due_Amount == a.Invoice_Amount:
				full_due_inv = full_due_inv + a.Invoice_Amount
				fdc = fdc + 1
			elif a.Due_Amount == 0:
				full_clear_inv = full_clear_inv + a.Invoice_Amount
				fcc = fcc + 1
			elif a.Due_Amount > 0 and a.Due_Amount != a.Invoice_Amount:
				part_due_inv = part_due_inv + a.Due_Amount
				pdc = pdc + 1
			else:
				pass
		if pay:
			total_paid = total_paid+sum(pay.values_list('Paid_Amount',flat=True))

	count = {'fdc':fdc, 'pdc':pdc, 'fcc':fcc, 'tbc':tbc}
	# total_paid = total_billing-full_due_inv-part_due_inv
	heads = {'full_due_inv':full_due_inv, 'part_due_inv':part_due_inv, 'full_clear_inv':full_clear_inv, 'total_billing':total_billing, 'total_paid':total_paid}
	table_items  = zip(pos_list, invoices_list)	
	
	return render(request, 'products/VendorInvoicesList.html', {'table':table_data, 'table_items':table_items, 'count':count, 'heads':heads, 
		'filter_data':filter_data, 'pdata':pdata, 'status':status, 'form':form})

# @login_required
# def Vendor_Payments_List(request, proj, status):
#   pdata = projectname(request, proj)
#   lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
#   lookup1 = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}

#   total, estimate, received, due, overdue, advance= 0,0,0,0,0,0
#   form = VendorPaymentForm()
#   form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0, Lock_Status=1, Final_Status=0)
#   form.fields["Invoice_No"].queryset = Vendor_Invoices.objects.filter(**lookup1, Due_Amount__gt=0)
  
#   table_pays = Vendor_Payment_Status.objects.filter(**lookup1).order_by('Payment_Date')
#   table_fy_pays = Vendor_Payment_Status.objects.filter(**lookup1, Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date()).order_by('Payment_Date')
  
#   filter_data = VendorPaymentsFilter(request.GET, queryset=table_fy_pays)
#   table_fy_pays = filter_data.qs
#   table_data = table_fy_pays
#   has_filter_pays = any(field in request.GET for field in set(filter_data.get_fields()))
  
#   if has_filter_pays: #update filter data queyset
#     filter_data = VendorPaymentsFilter(request.GET, queryset=table_pays)
#     table_pays = filter_data.qs
#     table_data = table_pays

#   pays_list, bills_list, t_rec, t_due, adv, t_billed, due_date, isallbill_clear, t_adv, advances, = [], [], [], [], [], [], [], [], 0, 0
#   t_due_all, t_due_overdue, t_due_unbilled, t_due_coming, total_billed, total_balance_as_advance = 0,0,0,0,0, 0

#   po_table_data = []
#   for x in table_data:
#     po_table_data.append(Purchases.objects.get(id=x.PO_No.id))

#   po_table_data = list(dict.fromkeys(po_table_data))
  
#   for x in po_table_data:
#     pays   = Vendor_Payment_Status.objects.filter(PO_No=x).order_by('Payment_Date')
#     bills    = Vendor_Invoices.objects.filter(PO_No=x).order_by('Invoice_Date')
#     for p in pays:
#       if p.Payment_Type=='Advance':
#         t_adv = t_adv + p.Paid_Amount
#     if pays:
#       pays_list.append(pays)
#       rec = pays.aggregate(sum=Sum('Paid_Amount')).get('sum') or 0
#       t_rec.append(rec)
#       for k in pays:
#         ad = 'True' if k.Payment_Type=='Advance' else 'False'
#         if ad == 'True':
#           break 
#       adv.append(ad)
#     else:
#       pays_list.append(None)
#       t_rec.append(0)
#       rec = 0

#     if bills:
#       billtotal = bills.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0
#       bills_list.append(bills)
#       t_due.append(bills.aggregate(sum=Sum('Due_Amount')).get('sum') or 0)
#       t_billed.append(billtotal)
      
#       for j in bills: #if all bills clear no need to show note text as coming due date etc..
#         dt = 'False' if j.Due_Amount==0 else 'True'
#         if dt == 'True':
#           break
#       if dt=='True': #means all bills not clear
#         for j in bills:
#           dt = 'True' if j.Payment_Over_Due_Days==0 else 'False'
#           if dt == 'True':
#             break
      
#       for n in bills:
#         clr = 'False' if n.Due_Amount!=0 else 'True'
#         if clr == 'False':
#           break

#       due_date.append(dt)
#       isallbill_clear.append(clr)
#     else:
#       bills_list.append(None)
#       t_due.append(None)
#       due_date.append(None)
#       t_billed.append(None)
#       isallbill_clear.append(None)
#       billtotal = 0

#     advances = advances + t_adv
#     t_adv=0

#     due_overdue = 0
#     due_coming = 0
#     for d in bills:
#       if d.Payment_Over_Due_Days > 0:
#         due_overdue = due_overdue+d.Due_Amount
#       else:
#         due_coming = due_coming+d.Due_Amount


#     t_due_overdue = t_due_overdue + due_overdue
#     t_due_coming = t_due_coming + due_coming
#     total_billed = total_billed + billtotal

#     if billtotal < rec:
#       total_balance_as_advance = total_balance_as_advance + rec - billtotal

#   # t_due_unbilled = t_orders_value - total_billed - total_balance_as_advance
#   t_due_all = t_due_overdue + t_due_coming
#   pc = {'t_due_all':t_due_all, 't_due_overdue':t_due_overdue, 't_due_coming':t_due_coming,'total_balance_as_advance':total_balance_as_advance}

#   data = zip(po_table_data, pays_list, bills_list, t_rec, t_due, adv, t_billed, due_date, isallbill_clear)
#   total_rec = sum(t_rec) or 0
#   billed_rec = total_rec - total_balance_as_advance
  
#   return render(request, 'products/VendorPaymentsList.html', {'table':table_data, 'data':data, 'filter_data':filter_data, 
#     'pdata':pdata, 'status':status, 'pc':pc, 'total_rec':total_rec, 'billed_rec':billed_rec, 'advances':advances, 'form_payments':form})

@login_required
def Vendor_Payments_List(request, proj, status, vendflt):
  pdata = projectname(request, proj)
  lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
  lookup1 = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}

  form = VendorPaymentForm()
  form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0, Lock_Status=1, Final_Status=0)
  form.fields["Invoice_No"].queryset = Vendor_Invoices.objects.filter(**lookup1, Due_Amount__gt=0)

  if vendflt != 'vendflt':
  	form.fields["Invoice_No"].queryset = Vendor_Invoices.objects.filter(PO_No__Vendor__Supplier_Name=vendflt, Due_Amount__gt=0)
  vendors = VendDt.objects.filter(Status=1, ds=1)
  

  table_data = Vendor_Payment_Status.objects.filter(**lookup1).order_by('-Payment_Date')
  # table_fy_pays = Vendor_Payment_Status.objects.filter(**lookup1, Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date()).order_by('Payment_Date')
  

  # ins = Vendor_Invoices.objects.all()
  # for v in ins:
  # 	v.Payment_Status = None
  # 	v.Due_Amount = v.Invoice_Amount
  # 	v.Payment_Cleared_Date = None
  # 	v.save()

  # for x in Vendor_Payment_Status.objects.all():
  # 	assign_paystatus_to_po(request, x.id, 'edit')
  # return HttpResponse('payments update')


  filter_data = VendorPaymentsFilter1(request.GET, queryset=table_data)
  table_data = filter_data.qs
  has_filter_pays = any(field in request.GET for field in set(filter_data.get_fields()))
 
  total_billed, total_paid, total_due, advances, vendors = 0,0,0,0,[]
  
  if has_filter_pays: #update filter data queyset
  	for x in table_data: vendors.append(x.PO_No.Vendor)
  	vendors = list(dict.fromkeys(vendors))
  else:
    for x in Purchases.objects.filter(**lookup, Lock_Status=1): vendors.append(x.Vendor)
    vendors = list(dict.fromkeys(vendors))
  
  for x in vendors:
			inv_list = Vendor_Invoices.objects.filter(**lookup1, PO_No__Vendor=x)
			pay_list = Vendor_Payment_Status.objects.filter(**lookup1, PO_No__Vendor=x)
			if inv_list:
				total_billed = total_billed + sum(inv_list.values_list('Invoice_Amount', flat=True))
				total_due = total_due + sum(inv_list.values_list('Due_Amount', flat=True))
			if pay_list:
				total_paid = total_paid + sum(pay_list.values_list('Paid_Amount', flat=True))
	
  advance = total_due - (total_billed - total_paid)
  # total_due = total_billed - total_paid
  # print(due, total_due)

  return render(request, 'products/VendorPaymentsList.html', {'table':table_data, 'filter_data':filter_data, 
    'pdata':pdata, 'status':status, 'total_billed':total_billed, 'total_paid':total_paid, 'total_due':total_due, 'advance':advance, 'form_payments':form, 'vendors':vendors, 'vendflt':vendflt})


@login_required
def Gen_PO(request, proj, fnc, poid, itemid, msg):
	pdata = projectname(request, proj)
	last_poid = Purchases.objects.filter(Lock_Status=1, Is_Manual=0, Is_No_PO=0).last()
	last_poid = last_poid.id if last_poid != None else None
	if request.method == 'POST' and fnc=='create':
		form = PurchasesForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			poid = p.id
			p.Related_Project = pdata['pj']
			p.save()
			genPO_initial_dataload(request, p.id, last_poid)
			msg = 'Basic Purchase Order Generated Successfully. Add Items to Purchase and Other Details to Generate PO Completely'
			url = '/'+str(pdata['pj'])+'/po/edit/'+str(p.id)+'/itemid/'+msg+'/'
			return redirect(url)

	if fnc == 'create_manually':		
		if request.method == 'POST':
			form = ManualPurchasesForm(request.POST, request.FILES)
			if form.is_valid():
				p = form.save()
				p.Related_Project, p.Is_Manual, p.Lock_Status = pdata['pj'], 1, 1
				p.save()
				messages.success(request, 'PO Has Been Added Successfully')
				return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])
		else:
			form = ManualPurchasesForm()
			form.fields["Vendor"].queryset = VendDt.objects.filter(Address_Type='Billing')
			return render(request, 'products/POForm.html', {'form': form, 'pdata':pdata})

	po = Purchases.objects.get(id=poid)
	form_po = PurchasesForm(instance=get_object_or_404(Purchases, id=po.id))
		
	items = Copy_PO_Items.objects.filter(PO_No = po)
	amount, total_gst, total_amount, final_gst, final_without_tax_amount, final_with_tax_amount = [],[],[],[],[],[] 
	if items:
		for x in items:
			amount.append(x.Quantity*x.Unit_Price)
			total_gst.append(x.Quantity*x.Unit_Price*x.GST/100)
			total_amount.append((x.Quantity*x.Unit_Price)+(x.Quantity*x.Unit_Price*x.GST/100))
		final_gst, final_without_tax_amount, final_with_tax_amount = int(sum(total_gst)), sum(amount), int(sum(total_amount))

	itm = zip(items, amount, total_gst, total_amount)
	ss = {'final_gst':final_gst, 'final_without_tax_amount':final_without_tax_amount, 'final_with_tax_amount':final_with_tax_amount}
	tc = PO_Terms_Conditions.objects.filter(PO_No=po).last()
	
	if PO_Terms_Conditions.objects.filter(PO_No=po).last():
		form_tc = POTCForm(instance=get_object_or_404(PO_Terms_Conditions, PO_No=po))
	else:
		form_tc = POTCForm()

	if itemid != 'itemid':
		form_item = CopyPOItemsForm(instance=get_object_or_404(Copy_PO_Items, id=itemid))
	else:
		form_item = POItemsForm()

	amount_in_words =  num2words(int(po.PO_Value), to='cardinal', lang='en_IN').replace(',', '').replace('-', ' ') if po.PO_Value else None 
	return render(request, 'docformats/PO1.html', {'pdata':pdata, 'po':po, 'itm':itm, 'ss':ss, 'tc':tc, 'form_po':form_po,
		'form_tc':form_tc, 'amount_in_words':amount_in_words, 'item_id':itemid, 'form_item':form_item, 'fnc':fnc, 'msg':msg})
	
@login_required
def Edit_PO_Form(request, proj, fnc, poid):
	pdata = projectname(request, proj)
	# po_id = Purchases.objects.get(id=poid).id
	msg='msg'
	url = '/'+str(pdata['pj'])+'/po/edit/'+str(poid)+'/itemid/'
	
	if request.method == 'POST':
		form = PurchasesForm(request.POST, request.FILES, instance=get_object_or_404(Purchases, id=poid))
		if form.is_valid():
			p= form.save()
			# updateduedays(request, p.Invoice_No)			
			
			if p.Lock_Status == 1:
				msg = "PO Has Been Locked and Generated Successfully"
				if update_po_amount(request, p.id) == 0:
					msg = "No Items Added in List of Items. Please Add Items to Complete PO"
					p.Lock_Status = 0
					p.save()
					url = url+msg+'/'
					return redirect(url)
			else:
				msg = "Requested Details Has Been Updated Successfully"
			url = url+msg+'/'	
			return redirect(url)
		else:
			url = url+msg+'/'
			return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			Purchases.objects.get(id=poid).delete()
			return redirect('/%s/purchaseslist/Inprogress/'%pdata['pj'])
		else:
			return redirect(url)

@login_required
def Edit_Vendor_Invoice_Form(request, proj, fnc, invid):
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg='msg'
	url = '/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'
	
	if request.method == 'POST':
		form = InvoicesForm(request.POST, request.FILES, instance=get_object_or_404(Invoices, id=invid))
		if form.is_valid():
			p= form.save()
			updateduedays(request, p.Invoice_No)
			#update when invoice locked
			if inv_amount_exceed(request, inv_order_id, p.Invoice_Amount)==1:
				p.Lock_Status = 0
				p.save()
				msg = 'Invoice generation not allowed due to all Invoices value under this order exceeding the order value'
				url = url+msg+'/'
				return redirect(url)

			if p.Is_Proforma == 1: #lock status meant for main invoice
				p.Lock_Status = 1
				p.save()
						
			order = Orders.objects.get(id=p.Order.id)
			if p.Lock_Status==1 and p.Is_Proforma==0:
				order.Billing_Status = p
				k = adjust_payments_to_invoices(request, order.id)
			else:
				# last order billing status opdate
				inv = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).last()
				order.Billing_Status = inv

			inv = Invoices.objects.filter(Order=p.Order, Lock_Status=1, Is_Proforma=0)
			order.Is_Billed = 1 if inv != None else 0
			order.save()
			
			if p.Lock_Status == 1:
				msg = "Invoice Has Been Locked and Generated Successfully"
			else:
				msg = "Requested Details Has Been Updated Successfully"

			url = url+msg+'/'	
			return redirect(url)
		else:
			url = url+msg+'/'
			return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			Invoices.objects.get(id=invid).delete()
			return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])
		else:
			return redirect(url)



@login_required
def Add_PO_Item_Form(request, proj, fnc, poid, itemid):
	pdata = projectname(request, proj)
	msg = 'msg'
	url = '/'+str(pdata['pj'])+'/po/edit/'+poid+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = CopyPOItemsForm(request.POST, request.FILES, instance=get_object_or_404(Copy_PO_Items, id=itemid))
			if form.is_valid():
				p= form.save()
				# inv_amoumt_update(request, invid)
				msg = "Item Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
		else:
			form = POItemsForm(request.POST, request.FILES)
			if form.is_valid():
				p = form.save()
				p.PO_No = Purchases.objects.get(id=poid)
				p.save()
				if PO_Items.objects.filter(PO_No=p.PO_No, Add_Item=p.Add_Item).order_by('id').count() > 1:
					PO_Items.objects.filter(PO_No=p.PO_No, Add_Item=p.Add_Item).order_by('id').last().delete()
					msg = "This Item Aleady Added, You Can Modify Quantity from Existing Items List"
					url = url+msg+'/'
					return redirect(url)
				else:
					copy_item = Copy_PO_Items.objects.create(PO_No=p.PO_No, Item_Description=p.Add_Item.Product_Name.Product_Name, Quantity=p.Quantity, UOM=p.Add_Item.Product_Name.UOM,
				Unit_Price=p.Add_Item.Unit_Price, HSN_Code=p.Add_Item.HSN_Code, GST=p.Add_Item.GST, 
				CESS=p.Add_Item.CESS, Other_Taxes=p.Add_Item.Other_Taxes, Item_From_Product=p)
				# inv_amoumt_update(request, invid)
				msg = "Item Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			copy_item = Copy_PO_Items.objects.get(id=itemid)
			item = PO_Items.objects.filter(Add_Item__Product_Name__Product_Name=copy_item.Item_From_Product.Add_Item.Product_Name.Product_Name)
			copy_item.delete()
			item.delete()
			# inv_amoumt_update(request, invid)
			return redirect(url)
		else:
			return redirect(url)

@login_required
def PO_TC_Form(request, proj, fnc, poid):
	pdata = projectname(request, proj)
	po = Purchases.objects.get(id=poid)
	msg = 'msg'
	url = '/'+str(pdata['pj'])+'/po/edit/'+poid+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = POTCForm(request.POST, request.FILES, instance=get_object_or_404(PO_Terms_Conditions, id=po.Terms_and_Conditions.id))
			if form.is_valid():
				p= form.save()
				msg = "Terms and Condition Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
		else:
			form = POTCForm(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				p.PO_No = po
				p.save()
				po.Terms_and_Conditions = p
				po.save()
				msg = "Terms and Condition Details Has Been Added Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			tc = PO_Terms_Conditions.objects.get(id=po.Terms_and_Conditions.id)
			tc.delete()
			return redirect(url)
		return redirect(url)

@login_required
def Products_Form(request, proj, fnc, status, prid):
	pdata = projectname(request, proj)
	if fnc != 'create':
		pid = Product_Price.objects.get(id=prid).Product_Name.id

	if fnc == 'edit':
		if request.method == 'POST':
			form1 = ProductsForm1(request.POST, request.FILES, instance=get_object_or_404(Products, id=pid), prefix='product')
			form2 = ProductsPriceForm(request.POST, instance=get_object_or_404(Product_Price, id=prid), prefix='productprice')
			if form1.is_valid() * form2.is_valid():
				p1 = form1.save()
				if status == 'Services':
					p1.Product_Type = 'Services'
					p1.save()
				p2 = form2.save()
				p2.Product_Name = p1
				p2.save()
				messages.success(request, "Product Details Has Been Updated")
				url = '/'+str(pdata['pj'])+'/productslist/'+status+'/'
				return redirect(url)
			else:
				url = '/'+str(pdata['pj'])+'/productslist/'+status+'/'
				return redirect(url)
		else:
			form1 = ProductsForm1(instance=get_object_or_404(Products, id=pid), prefix='product')
			form2 = ProductsPriceForm(instance=get_object_or_404(Product_Price, id=prid), prefix='productprice')
			return render(request, 'products/ProductsForm.html', {'form1': form1, 'form2': form2, 'pdata':pdata, 'status':status})
	elif fnc == 'delete':
		product = Products.objects.get(id=pid)
		productprice = Product_Price.objects.get(id=prid)
		product.delete()
		productprice.delete()
		messages.success(request, "Product Has Been Deleted")
		url = '/'+str(pdata['pj'])+'/productslist/'+status+'/'
		return redirect(url)
	else:
		if request.method == 'POST':
			form1 = ProductsForm(request.POST, request.FILES, prefix='product')
			form2 = ProductsPriceForm(request.POST, prefix='productprice')
			if form1.is_valid() * form2.is_valid():
				p1 = form1.save()
				if status == 'Services':
					p1.Product_Type = 'Services'
					p1.save()
				p2 = form2.save()
				p2.Product_Name = p1
				p2.save()
				messages.success(request, "Product Has Been Created")
				url = '/'+str(pdata['pj'])+'/productslist/'+status+'/'
				return redirect(url)
			else:
				url = '/'+str(pdata['pj'])+'/productslist/'+status+'/'
				return redirect(url)
		else:
			if fnc == 'copy':
				form1 = ProductsForm(instance=get_object_or_404(Products, id=pid), prefix='product')
				form2 = ProductsPriceForm(instance=get_object_or_404(Product_Price, id=prid), prefix='productprice')
				return render(request, 'products/ProductsForm.html', {'form1': form1, 'form2': form2, 'pdata':pdata, 'status':status})
			else:
				form1 = ProductsForm(prefix='product')
				form2 = ProductsPriceForm(prefix='productprice')
				return render(request, 'products/ProductsForm.html', {'form1': form1, 'form2': form2, 'pdata':pdata, 'status':status})

@login_required
def Products_List(request, proj, status):
	pdata = projectname(request, proj)
	table = Product_Price.objects.filter(Product_Name__Status=1)
	filter_data = ProductsFilter(request.GET, queryset=table)
	table = filter_data.qs
	if status == 'Products':
		table = table.filter(Q(Product_Name__Product_Type='Finished Goods')|Q(Product_Name__Product_Type='Raw Material'))
	else:
		table = table.filter(Product_Name__Product_Type='Services')
	count = len(table)
	return render(request, 'products/ProductsList.html', {'table':table, 'pdata':pdata, 'status':status, 'count':count})

@login_required
def Stock_Movement_Form(request, proj, fnc, pid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = StockMovementForm(request.POST, request.FILES, instance=get_object_or_404(Product_Movement, id=pid))
			if form.is_valid():
				p= form.save()
				messages.success(request, "Stock Has Been Updated")
				return redirect('/%s/inventory/active/'%pdata['pj'])
			else:
				return redirect('/%s/inventory/active/'%pdata['pj'])
		else:
			form = StockMovementForm(instance=get_object_or_404(Product_Movement, id=pid))
			return render(request, 'products/StockMovementForm.html', {'form': form, 'pdata':pdata})
	elif fnc == 'delete':
		product = Product_Movement.objects.get(id=pid)
		product.delete()
		messages.success(request, "Stock Has Been Deleted")
		return redirect('/%s/inventory/active/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = StockMovementForm(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				messages.success(request, "Stock Has Been Updated")
				return redirect('/%s/inventory/active/'%pdata['pj'])
			else:
				return redirect('/%s/inventory/active/'%pdata['pj'])
		else:
			if fnc == 'copy':
				form = StockMovementForm(instance=get_object_or_404(Product_Movement, id=pid))
				return render(request, 'products/StockMovementForm.html', {'form': form, 'pdata':pdata})
			else:
				form = StockMovementForm()
				return render(request, 'products/StockMovementForm.html', {'form': form, 'pdata':pdata})

@login_required
def Inventory_List(request, proj, status):
	pdata = projectname(request, proj)
	return HttpResponse(pdata)


@login_required
def Quotation_List(request, proj, status):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	if status == 'all':
		table = Quotes.objects.filter(**lookup, Lock_Status=1)
	else:
		table = Quotes.objects.filter(**lookup, Lock_Status=0)

	print(table)

	return render(request, 'quotations/QuotationsList.html', {'pdata':pdata, 'table':table, 'status':status})

@login_required
def Quotation_Form(request, proj, fnc, qid):
	pdata = projectname(request, proj) 	
	if request.method == 'POST':
		form = QuotationForm(request.POST)
		if form.is_valid():
			p = form.save()
			p.Related_Project = pdata['pj']
			p.Prepared_By = Account.objects.get(user=request.user)
			p.Date = date.today()
			p.Quote_Submitted_By = Account.objects.get(user=request.user)
			p.save()
			
			messages.success(request, 'Quotation Added Successfully')
			return redirect('/%s/quotationslist/'%pdata['pj'])
		else:
			return redirect('/%s/quotationslist/'%pdata['pj'])
	else:
		form = QuotationForm()
		return render(request, 'quotations/QuotationsForm.html', {'form': form, 'pdata':pdata})

@login_required
def Gen_Quotation(request, proj, fnc, qid, itemid, msg):
	pdata = projectname(request, proj)
	# last_poid = Purchases.objects.filter(Lock_Status=1, Is_Manual=0, Is_No_PO=0).last()
	# last_poid = last_poid.id if last_poid != None else None

	if fnc == 'create':		
		if request.method == 'POST':
			form = QuotationForm(request.POST)
			if form.is_valid():
				p = form.save()
				p.Related_Project = pdata['pj']
				p.Prepared_By = Account.objects.get(user=request.user)
				p.Date = date.today()
				p.Quote_Submitted_By = Account.objects.get(user=request.user)
				# p.Thanks_Note = 'Thanking you and assuring you of our best services at all times'
				p.Reference_Person = p.Quote_To.Contact_Person if p.Quote_To.Contact_Person != None else None
				p.Phone_Number = p.Quote_To.Phone_Number_1 if p.Quote_To.Phone_Number_1 != None else None
				p.Email = p.Quote_To.Email if p.Quote_To.Email != None else None
				p.Firm_Name = p.Quote_To.Customer_Name.Customer_Name if p.Quote_To.Customer_Name != None else None
				p.save()
				tc = Quote_TC_Default.objects.all().last()
				Quote_TC.objects.create(Quote_No=p, Taxes=tc.Taxes, Payment_Terms=tc.Payment_Terms, Delivery_Terms=tc.Delivery_Terms, 
					Transport_Terms=tc.Transport_Terms, Validation_Terms=tc.Validation_Terms, FOR=tc.FOR, Other_Terms=tc.Other_Terms) if tc != None else None
				p.Quote_From = CompanyDetails.objects.all().last()
				p.save()
				msg = 'Basic Quotation Generated Successfully. Add Further Details and Items to Complete'
				url = '/'+str(pdata['pj'])+'/genquote/edit/'+str(p.id)+'/itemid/'+msg+'/'
				return redirect(url)
			else:
				url = '/'+str(pdata['pj'])+'/genquote/create/1/itemid/msg/'
				return redirect(url)
		else:
			form = QuotationForm()
			return render(request, 'quotations/QuotationsForm.html', {'form': form, 'pdata':pdata})

	qt = Quotes.objects.get(id=qid)
	form_qt = QuotationEditForm(instance=get_object_or_404(Quotes, id=qt.id))

	items = Copy_Quote_Items.objects.filter(Quote_No = qt)
	amount, total_gst, total_amount, final_gst, final_without_tax_amount, final_with_tax_amount = [],[],[],[],[],[] 
	if items:
		for x in items:
			amount.append(x.Quantity*x.Unit_Price)
			# total_amount.append((x.Quantity*x.Unit_Price)+(x.Quantity*x.Unit_Price*x.GST/100))
		final_without_tax_amount = sum(amount)
	itm = zip(items, amount)
	ss = {'final_without_tax_amount':final_without_tax_amount}
	tc = Quote_TC.objects.filter(Quote_No=qt).last()	
	if Quote_TC.objects.filter(Quote_No=qt).last():
		form_tc = QuoteTCForm(instance=get_object_or_404(Quote_TC, Quote_No=qt))
	else:
		form_tc = QuoteTCForm()

	if itemid != 'itemid':
		form_item = CopyQuoteItemsForm(instance=get_object_or_404(Copy_Quote_Items, id=itemid))
	else:
		form_item = QuoteItemsForm()

	form_fileupload = QuoteFileForm()

	refpo = 0
	for x in items:
		if x.Ref_PO != None:
			refpo = 1
			break
			
	amount_in_words =  num2words(int(qt.Quote_Value), to='cardinal', lang='en_IN').replace(',', '').replace('-', ' ') if qt.Quote_Value else None 
	return render(request, 'docformats/quotation1.html', {'pdata':pdata, 'qt':qt, 'itm':itm, 'ss':ss, 'tc':tc, 'form_qt':form_qt, 'form_fileupload':form_fileupload,
		'form_tc':form_tc, 'amount_in_words':amount_in_words, 'item_id':itemid, 'form_item':form_item, 'fnc':fnc, 'msg':msg, 'refpo':refpo})

@login_required
def Edit_Quotation_Form(request, proj, fnc, qid):
	pdata = projectname(request, proj)
	msg='msg'
	url = '/'+str(pdata['pj'])+'/genquote/edit/'+str(qid)+'/itemid/'
	
	if request.method == 'POST':
		form = QuotationEditForm(request.POST, request.FILES, instance=get_object_or_404(Quotes, id=qid))
		if form.is_valid():
			p= form.save()
			# updateduedays(request, p.Invoice_No) 			
			
			if p.Lock_Status == 1:
				msg = "Quote Has Been Locked and Generated Successfully"
				if update_qt_amount(request, p.id) == 0:
					msg = "No Items Added in List of Items. Please Add Items to Complete Quote"
					p.Lock_Status = 0
					p.save()
					url = url+msg+'/'
					return redirect(url)
			else:
				msg = "Requested Details Has Been Updated Successfully"
			url = url+msg+'/'	
			return redirect(url)
		else:
			url = url+msg+'/'
			return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			Quotes.objects.get(id=qid).delete()
			return redirect('/%s/quotationslist/all/'%pdata['pj'])
		else:
			return redirect(url)

@login_required
def Add_Quotation_Item_Form(request, proj, fnc, qid, itemid):
	pdata = projectname(request, proj)
	msg = 'msg'
	url = '/'+str(pdata['pj'])+'/genquote/edit/'+qid+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = CopyQuoteItemsForm(request.POST, request.FILES, instance=get_object_or_404(Copy_Quote_Items, id=itemid))
			if form.is_valid():
				p= form.save()
				update_qt_amount(request, qid)
				msg = "Item Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
		else:
			form = QuoteItemsForm(request.POST, request.FILES)
			if form.is_valid():
				p = form.save()
				p.Quote_No = Quotes.objects.get(id=qid)
				p.save()
				if Quote_Items.objects.filter(Quote_No=p.Quote_No, Add_Item=p.Add_Item).order_by('id').count() > 1:
					Quote_Items.objects.filter(Quote_No=p.Quote_No, Add_Item=p.Add_Item).order_by('id').last().delete()
					msg = "This Item Aleady Added, You Can Modify Quantity from Existing Items List"
					url = url+msg+'/'
					return redirect(url)
				else:
					copy_item = Copy_Quote_Items.objects.create(Quote_No=p.Quote_No, Item_Description=p.Add_Item.Product_Name.Product_Name, Quantity=p.Quantity, UOM=p.Add_Item.Product_Name.UOM,
				Unit_Price=p.Add_Item.Unit_Price, GST=p.Add_Item.GST, Item_From_Product=p, HSN_Code=p.Add_Item.HSN_Code)
				update_qt_amount(request, qid)
				msg = "Item Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			copy_item = Copy_Quote_Items.objects.get(id=itemid)
			if copy_item.Item_From_Product:
				item = Quote_Items.objects.filter(Add_Item__Product_Name__Product_Name=copy_item.Item_From_Product.Add_Item.Product_Name.Product_Name)
				item.delete()
			copy_item.delete()
			update_qt_amount(request, qid)
			return redirect(url)
		else:
			return redirect(url)

@login_required
def Quotation_TC_Form(request, proj, fnc, qid):
	pdata = projectname(request, proj)
	qt = Quotes.objects.get(id=qid)
	msg = 'msg'
	url = '/'+str(pdata['pj'])+'/genquote/edit/'+qid+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = QuoteTCForm(request.POST, request.FILES, instance=get_object_or_404(Quote_TC, id=Quote_TC.objects.filter(Quote_No=qt).last().id))
			if form.is_valid():
				p= form.save()
				msg = "Terms and Condition Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
		else:
			form = QuoteTCForm(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				p.Quote_No = qt
				p.save()
				msg = "Terms and Condition Details Has Been Added Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			tc = Quote_TC.objects.get(id=Quote_TC.objects.filter(Quote_No=qt).last().id)
			tc.delete()
			return redirect(url)
		return redirect(url)

import pandas as pd
@login_required
def Upload_Quote(request, proj, qid):
	qt = Quotes.objects.filter(id=qid).last()
	pdata = projectname(request, proj)
	data = None
	if request.method == 'POST':
	  file_form = QuoteFileForm(request.POST, request.FILES)
	  raw_file= request.FILES
	  if file_form.is_valid():       
	    data = request.FILES['Attach']             
	    data = pd.read_excel(data, header=0)
	    for x in data.itertuples():
	    	try:
		    	if x.Item_Description != None and x.Quantity != None and x.UOM != None and x.Unit_Price != None:
		    		if isinstance(x.Quantity, int) or isinstance(x.Quantity, float):
		    			if isinstance(x.Unit_Price, int) or isinstance(x.Unit_Price, float):
		    				Copy_Quote_Items.objects.create(Quote_No=qt, Item_Description=x.Item_Description, Quantity=x.Quantity, UOM=x.UOM, Unit_Price=x.Unit_Price, HSN_Code=x.HSN_Code, Ref_PO=x.Ref_PO)
	    	except:
	    		return render(request, 'products/quotefileuploaderror.html', {'qid':qid, 'pdata':pdata})

	    update_qt_amount(request, qid)
	    url = '/'+str(pdata['pj'])+'/genquote/edit/'+qid+'/itemid/msg/'
	    return redirect(url)
	  else:
	  	return render(request, 'products/quotefileuploaderror.html', {'qid':qid, 'pdata':pdata})
	else:
		form = QuoteFileForm()
		return render(request,'products/upload.html', {'form':form, 'pdata':pdata})	






