from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import *
from .forms import *
from .filters import *
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date, datetime, timedelta 
from django.db.models import Sum, Avg, Count
from django.contrib.auth.decorators import login_required
from UserAccounts.models import *
from .basedata import projectname


@login_required
def Select_Project(request):
	pdata = projectname(request, None)
	return render(request, 'projects/SelectProject.html', {'pdata':pdata})
	# return render(request, 'proposals/ContactUs.html', {'pdata':pdata})

@login_required
def Select_Module(request, proj):
	pdata = projectname(request, proj)
	return render(request, 'projects/SelectModule.html', {'pdata':pdata})

@login_required
def CustDt_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(CustDt, id=rid)
			form = CustomerForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				form.save()
				messages.success(request, "Selected Customer Details Has Been Updated")
				return redirect('/%s/customerslist/'%pdata['pj'])
			else:
				return render(request, 'projects/CustDtForm.html.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(CustDt, id=rid)
			form = CustomerForm(instance=getdata)
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(CustDt, id=rid)
		getdata.ds = 0
		getdata.save()
		messages.success(request, "Selected Customer Details Has Been Send to Recyclebin")
		return redirect('/%s/customerslist/'%pdata['pj'])

	if request.method ==  'POST': #Create
		form = CustomerForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, "Customer Details Has Been Added")
			return redirect('/%s/customerslist/'%pdata['pj'])
		else:
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(CustDt, id=rid)
			form = CustomerForm(instance=getdata)
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata})
		else:
			form = CustomerForm()
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata})

@login_required
def CustDt_List(request, proj):
	pdata = projectname(request, proj)
	contact_person = []
	table = CustDt.objects.filter(ds=1)
	filter_data = CustomerFilter(request.GET, queryset=table)
	table = filter_data.qs
	for x in table:
		p = CustContDt.objects.filter(Customer_Name=x, ds=1)
		contact_person.append(p if p else None)
	data = zip(table, contact_person)
	return render(request, 'projects/CustDtList.html', {'data':data, 'filter_data':filter_data, 'pdata':pdata})

@login_required
def CustContDt_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(CustContDt, id=rid)
			form = CustomerContactForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				form.save()
				messages.success(request, "Selected Customer Contact Details Has Been Updated")
				return redirect('/%s/customerslist/'%pdata['pj'])
			else:
				return render(request, 'projects/CustContDtForm.html.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(CustContDt, id=rid)
			form = CustomerContactForm(instance=getdata)
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(CustContDt, id=rid)
		getdata.ds = 0
		getdata.save()
		messages.success(request, "Selected Customer Contact Details Has Been Send to Recyclebin")
		return redirect('/%s/customerslist/'%pdata['pj'])

	if request.method ==  'POST': #Create
		form = CustomerContactForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, "Customer Contact Details Has Been Added")
			return redirect('/%s/customerslist/'%pdata['pj'])
		else:
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(CustContDt, id=rid)
			form = CustomerContactForm(instance=getdata)
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata})
		else:
			form = CustomerContactForm()
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata})


@login_required
def VendDt_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(VendDt, id=rid)
			form = VendorForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				form.save()
				messages.success(request, "Selected Vendor Details Has Been Updated")
				return redirect('/%s/vendorslist/'%pdata['pj'])
			else:
				return render(request, 'projects/VendDtForm.html.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(VendDt, id=rid)
			form = VendorForm(instance=getdata)
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(VendDt, id=rid)
		getdata.ds = 0
		getdata.save()
		messages.success(request, "Selected Vendor Details Has Been Send to Recyclebin")
		return redirect('/%s/vendorslist/'%pdata['pj'])

	if request.method ==  'POST': #Create
		form = VendorForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, "Vendor Details Has Been Added")
			return redirect('/%s/vendorslist/'%pdata['pj'])
		else:
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(VendDt, id=rid)
			form = VendorForm(instance=getdata)
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata})
		else:
			form = VendorForm()
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata})

@login_required
def VendDt_List(request, proj):
	pdata = projectname(request, proj)
	contact_person = []
	table = VendDt.objects.filter(ds=1)
	filter_data = VendorFilter(request.GET, queryset=table)
	table = filter_data.qs
	for x in table:
		p = VendContDt.objects.filter(Supplier_Name=x, ds=1)
		contact_person.append(p if p else None)
	data = zip(table, contact_person)
	return render(request, 'projects/VendDtList.html', {'data':data, 'filter_data':filter_data, 'pdata':pdata})

@login_required
def VendContDt_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(VendContDt, id=rid)
			form = VendorContactForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				form.save()
				messages.success(request, "Selected Vendor Contact Details Has Been Updated")
				return redirect('/%s/vendorslist/'%pdata['pj'])
			else:
				return render(request, 'projects/VendContDtForm.html.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(VendContDt, id=rid)
			form = VendorContactForm(instance=getdata)
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(VendContDt, id=rid)
		getdata.ds = 0
		getdata.save()
		messages.success(request, "Selected Vendor Contact Details Has Been Send to Recyclebin")
		return redirect('/%s/vendorslist/'%pdata['pj'])

	if request.method ==  'POST': #Create
		form = VendorContactForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, "Vendor Contact Details Has Been Added")
			return redirect('/%s/vendorslist/'%pdata['pj'])
		else:
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(VendContDt, id=rid)
			form = VendorContactForm(instance=getdata)
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata})
		else:
			form = VendorContactForm()
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata})


