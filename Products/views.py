from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from datetime import date, datetime, timedelta 
from django.http import HttpResponse, JsonResponse
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
from Projects.fyear import get_financial_year, get_fy_date
from Projects.basedata import projectname
from .customfunctions import genPO_initial_dataload, update_po_amount, assign_paystatus_to_po, adjust_payments_to_invoices, update_vendor_invoice, updateduedays, update_delivery_status
from num2words import num2words
from django.urls import reverse
 
@login_required
def PO_List(request, proj, status):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	# lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	table = Purchases.objects.filter(**lookup).order_by('-PO_Date')
	table_fy = Purchases.objects.filter(**lookup, PO_Date__date__lte=date.today(), PO_Date__date__gte=get_fy_date()).order_by('-PO_Date')

	form_select_vendor = PurchasesForm()
	
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
			paid=0
			for z in pays:
				paid = paid + z.Paid_Amount
			po_paid.append(int(paid))
		else:
			po_paid.append(0)

		if x.Delivery_Status:
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

	return render(request, 'products/OrdersForm.html', {'form': form, 'pdata':pdata})

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
			assign_paystatus_to_po(request, p.id, po.id)
			adjust_payments_to_invoices(request, po.id)
			messages.success(request, "Payment Has Been Added")
			return redirect('/%s/vendorpaymentslist/Paid/'%pdata['pj'])
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
        assign_paystatus_to_po(request, p.id, po.id)
        adjust_payments_to_invoices(request, po.id)
        messages.success(request, "Selected Payment Details Has Been Updated")
        return redirect('/%s/vendorpaymentslist/Paid/'%pdata['pj'])
      else:
        return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})
    else:
      getdata = get_object_or_404(Vendor_Payment_Status, id=payid)
      form = VendorPaymentForm1(instance=getdata)
      return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})

  elif fnc == 'delete': #Delete
    getdata = get_object_or_404(Vendor_Payment_Status, id=payid)
    po = getdata.PO_No
    getdata.delete()
    po = Purchases.objects.get(id=po.id)
    adjust_payments_to_invoices(request, po.id)
    if not po.Payment_Status:
      po.Payment_Status = Vendor_Payment_Status.objects.filter(PO_No=po).order_by('Payment_Date').last()
      po.save()
    messages.success(request, "Selected Payment Details Has Deleted")
    return redirect('/%s/vendorpaymentslist/Paid/'%pdata['pj'])

  if request.method ==  'POST': #Create
    form = VendorPaymentForm(request.POST, request.FILES)
    if form.is_valid():
      p = form.save(commit=False)
      if p.PO_No==None and p.Invoice_No==None:
        messages.error(request, "Either PO No or Invoice No Must Be Geiven to Record Payment")
        return redirect('/%s/vendorpaymentslist/Paid/'%pdata['pj'])
      p= form.save()
      if not p.PO_No: # when paymentbthrough invoice number
        p.PO_No = p.Invoice_No.PO_No
        p.save()
        assign_paystatus_to_po(request, p.id, p.PO_No.id)
      else:
        assign_paystatus_to_po(request, p.id, p.PO_No.id)
      po = Purchases.objects.get(id=p.PO_No.id)
      adjust_payments_to_invoices(request, po.id)
      messages.success(request, "Payment Has Been Added")
      return redirect('/%s/vendorpaymentslist/Paid/'%pdata['pj'])
    else:
      return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})
  else:
    if fnc == 'copy':
      getdata = get_object_or_404(Vendor_Payment_Status, id=payid)
      form = VendorPaymentForm(instance=getdata)
      return render(request, 'products/VendorPaymentsForm.html', {'form': form, 'pdata':pdata})
    else:
      form = VendorPaymentForm()
      form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0)
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
        adjust_payments_to_invoices(request, po.id)
        messages.success(request, "Selected Invoice Details Has Been Updated")
        return redirect('/%s/vendorinvoiceslist/Issued/'%pdata['pj'])
      else:
        return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata})
    else:
      getdata = get_object_or_404(Vendor_Invoices, id=invid)
      form = VendorInvoicesForm1(instance=getdata)
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata})

  elif fnc == 'delete': #Delete
    getdata = get_object_or_404(Vendor_Invoices, id=invid)
    po = getdata.PO_No
    getdata.delete()
    po = Purchases.objects.get(id=po.id)
    adjust_payments_to_invoices(request, po.id)
    if not po.Billing_Status:
      po.Billing_Status = Vendor_Invoices.objects.filter(PO_No=po).order_by('Invoice_Date').last()
      po.save()
    messages.success(request, "Selected Invoice Details Has Been Deleted")
    return redirect('/%s/vendorinvoiceslist/Issued/'%pdata['pj'])

  if request.method ==  'POST': #Create
    form = VendorInvoicesForm(request.POST, request.FILES)
    if form.is_valid():
      p= form.save()
      updateduedays(request, p.id)
      update_vendor_invoice(request, p.id, p.PO_No.id)
      adjust_payments_to_invoices(request, p.PO_No.id)
      messages.success(request, "Vendor Invoice Has Been Registered")
      return redirect('/%s/vendorinvoiceslist/Issued/'%pdata['pj'])
    else:
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata})
  else:
    if fnc == 'copy':
      getdata = get_object_or_404(Vendor_Invoices, id=invid)
      form = VendorInvoicesForm(instance=getdata)
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata})
    else:
      form = VendorInvoicesForm()
      form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0)
      return render(request, 'products/VendorInvoiceForm.html', {'form': form, 'pdata':pdata})

@login_required
def Vendor_Invoices_List(request, proj, status):
	pdata = projectname(request, proj)
	
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	form = VendorInvoicesForm()
	form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0)
	
	lookup = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}
	table_inv = Vendor_Invoices.objects.filter(**lookup).order_by('-Invoice_Date')
	table_fy_inv = Vendor_Invoices.objects.filter(**lookup, Invoice_Date__date__lte=date.today(), Invoice_Date__date__gte=get_fy_date()).order_by('-Invoice_Date')
	
	filter_data = VendorInvoicesFilter(request.GET, queryset=table_fy_inv)
	table_fy_inv = filter_data.qs
	table_data = table_fy_inv
	has_filter_inv = any(field in request.GET for field in set(filter_data.get_fields()))
	
	if has_filter_inv: #update filter data queyset
		filter_data = VendorInvoicesFilter(request.GET, queryset=table_inv)
		table_inv = filter_data.qs
		table_data = table_inv

	full_due_inv, part_due_inv, full_clear_inv, total_billing = 0, 0, 0, 0
	fdc, pdc, fcc, tbc = 0, 0, 0, 0 #count
	orders_list, invoices_list  = [], []

	pos_list = []
	
	for x in table_data:
		pos_list.append(x.PO_No)
	pos_list = list(dict.fromkeys(pos_list))

	for x in pos_list:
		inv = Vendor_Invoices.objects.filter(PO_No=x).order_by('Invoice_Date')
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
	count = {'fdc':fdc, 'pdc':pdc, 'fcc':fcc, 'tbc':tbc}
	heads = {'full_due_inv':full_due_inv, 'part_due_inv':part_due_inv, 'full_clear_inv':full_clear_inv, 'total_billing':total_billing}
	table_items  = zip(pos_list, invoices_list)	
	
	return render(request, 'products/VendorInvoicesList.html', {'table':table_data, 'table_items':table_items, 'count':count, 'heads':heads, 
		'filter_data':filter_data, 'pdata':pdata, 'status':status, 'form':form})

@login_required
def Vendor_Payments_List(request, proj, status):
  pdata = projectname(request, proj)
  lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
  lookup1 = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}

  total, estimate, received, due, overdue, advance= 0,0,0,0,0,0
  form = VendorPaymentForm()
  form.fields["PO_No"].queryset = Purchases.objects.filter(**lookup, Payment_Final_Status=0)
  form.fields["Invoice_No"].queryset = Vendor_Invoices.objects.filter(**lookup1, Due_Amount__gt=0)
  
  table_pays = Vendor_Payment_Status.objects.filter(**lookup1).order_by('Payment_Date')
  table_fy_pays = Vendor_Payment_Status.objects.filter(**lookup1, Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date()).order_by('Payment_Date')
  
  filter_data = VendorPaymentsFilter(request.GET, queryset=table_fy_pays)
  table_fy_pays = filter_data.qs
  table_data = table_fy_pays
  has_filter_pays = any(field in request.GET for field in set(filter_data.get_fields()))
  
  if has_filter_pays: #update filter data queyset
    filter_data = VendorPaymentsFilter(request.GET, queryset=table_pays)
    table_pays = filter_data.qs
    table_data = table_pays

  pays_list, bills_list, t_rec, t_due, adv, t_billed, due_date, isallbill_clear, t_adv, advances, = [], [], [], [], [], [], [], [], 0, 0
  t_due_all, t_due_overdue, t_due_unbilled, t_due_coming, total_billed, total_balance_as_advance = 0,0,0,0,0, 0

  po_table_data = []
  for x in table_data:
    po_table_data.append(Purchases.objects.get(id=x.PO_No.id))

  po_table_data = list(dict.fromkeys(po_table_data))
  
  for x in po_table_data:
    pays   = Vendor_Payment_Status.objects.filter(PO_No=x).order_by('Payment_Date')
    bills    = Vendor_Invoices.objects.filter(PO_No=x).order_by('Invoice_Date')
    for p in pays:
      if p.Payment_Type=='Advance':
        t_adv = t_adv + p.Paid_Amount
    if pays:
      pays_list.append(pays)
      rec = pays.aggregate(sum=Sum('Paid_Amount')).get('sum') or 0
      t_rec.append(rec)
      for k in pays:
        ad = 'True' if k.Payment_Type=='Advance' else 'False'
        if ad == 'True':
          break 
      adv.append(ad)
    else:
      pays_list.append(None)
      t_rec.append(0)
      rec = 0

    if bills:
      billtotal = bills.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0
      bills_list.append(bills)
      t_due.append(bills.aggregate(sum=Sum('Due_Amount')).get('sum') or 0)
      t_billed.append(billtotal)
      
      for j in bills: #if all bills clear no need to show note text as coming due date etc..
        dt = 'False' if j.Due_Amount==0 else 'True'
        if dt == 'True':
          break
      if dt=='True': #means all bills not clear
        for j in bills:
          dt = 'True' if j.Payment_Over_Due_Days==0 else 'False'
          if dt == 'True':
            break
      
      for n in bills:
        clr = 'False' if n.Due_Amount!=0 else 'True'
        if clr == 'False':
          break

      due_date.append(dt)
      isallbill_clear.append(clr)
    else:
      bills_list.append(None)
      t_due.append(None)
      due_date.append(None)
      t_billed.append(None)
      isallbill_clear.append(None)
      billtotal = 0

    advances = advances + t_adv
    t_adv=0

    due_overdue = 0
    due_coming = 0
    for d in bills:
      if d.Payment_Over_Due_Days > 0:
        due_overdue = due_overdue+d.Due_Amount
      else:
        due_coming = due_coming+d.Due_Amount


    t_due_overdue = t_due_overdue + due_overdue
    t_due_coming = t_due_coming + due_coming
    total_billed = total_billed + billtotal

    if billtotal < rec:
      total_balance_as_advance = total_balance_as_advance + rec - billtotal

  # t_due_unbilled = t_orders_value - total_billed - total_balance_as_advance
  t_due_all = t_due_overdue + t_due_coming
  pc = {'t_due_all':t_due_all, 't_due_overdue':t_due_overdue, 't_due_coming':t_due_coming,'total_balance_as_advance':total_balance_as_advance}

  data = zip(po_table_data, pays_list, bills_list, t_rec, t_due, adv, t_billed, due_date, isallbill_clear)
  total_rec = sum(t_rec) or 0
  billed_rec = total_rec - total_balance_as_advance
  
  return render(request, 'products/VendorPaymentsList.html', {'table':table_data, 'data':data, 'filter_data':filter_data, 
    'pdata':pdata, 'status':status, 'pc':pc, 'total_rec':total_rec, 'billed_rec':billed_rec, 'advances':advances, 'form_payments':form})


@login_required
def Gen_PO(request, proj, fnc, poid, itemid, msg):
	pdata = projectname(request, proj)
	last_poid = Purchases.objects.filter(Lock_Status=1).last()
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

	amount_in_words =  num2words(int(po.PO_Value), to='cardinal', lang='en_IN') if po.PO_Value else None 
	len_words = len(amount_in_words) if po.PO_Value else 0
	return render(request, 'docformats/PO1.html', {'pdata':pdata, 'po':po, 'itm':itm, 'ss':ss, 'tc':tc, 'form_po':form_po,
		'form_tc':form_tc, 'amount_in_words':amount_in_words, 'len_words':len_words, 
		'item_id':itemid, 'form_item':form_item, 'fnc':fnc, 'msg':msg})
	
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
			tc = p	=PO_Terms_Conditions.objects.get(id=po.Terms_and_Conditions.id)
			tc.delete()
			return redirect(url)
		return redirect(url)