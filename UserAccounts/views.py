from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Projects.basedata import projectname
from json import dumps
from datetime import date, datetime, timedelta 



from .forms import *

def get_errors(request, formerrors):
	x = 'Errors: '
	for field, errors in formerrors.items():
			x = x + ('{}'.format(','.join(errors))) + ' '
	return x

def update_salary_breaking(request, sid):
	p = Empl_Salaries.objects.get(id=sid)
	
	p.ESI_Amount = p.Basic*0.0075 if p.ESI_Eligibility == True else 0
	pf_per = 0.12 if p.Is_Providing_PF_Employer_Share == True else 0.24
	p.PF_Amount = p.Basic*pf_per if p.PF_Eligibility == True else 0
	p.Net_Salary = p.Gross_Salary-p.PF_Amount-p.ESI_Amount-0 #if p.Net_Salary == None else p.Net_Salary 
	
	if (p.Gross_Salary - p.Basic - p.PF_Amount - p.ESI_Amount - 0) >= p.Basic*0.4:
		p.HRA= p.Basic*0.4
	else:
		p.HRA = 0
	p.Other_Allowances = p.Gross_Salary-p.Basic-p.HRA-p.PF_Amount-p.ESI_Amount-0  #for now 0 is PT, it may 0-200
	if p.Other_Allowances < 0:
		p.Other_Allowances = 0
	if not p.Effective_From:
		p.Effective_From = date.today()
	if not p.Next_Revision_Date:
		join_dt = p.Employ_Name.Joining_Date
		p.Next_Revision_Date = date(join_dt.year+1, join_dt.month, join_dt.day) if join_dt != None else date(p.Effective_From.year+1, p.Effective_From.month, p.Effective_From.day)
	
	p.save()

def update_sal_revision(request, p):
	empl_sal = Empl_Salaries.objects.filter(Employ_Name=p.Employ_Name).last()
	# if not empl_sal:
	# 	messages.error(request,  "Before Revise Salary Please Register His Joining Salary Using Employ Salary Form")
	# 	return 'errormsg'
	# if p.Revised_Gross == empl_sal.Gross_Salary:
	# 	messages.error(request, "Revised Salary Must Not Be Same As Previous Salary")
	# 	return 'errormsg'
	# else:
	# 	p = form.save()

	
	if p.Revised_Basic == None:
		p.Revised_Basic = empl_sal.Basic
	# if p.Previous_Gross == empl_sal.Gross_Salary and p.Previous_Basic != empl_sal.Basic:
	# 	p.Next_Revision_Date = date(p.Previous_Date.year+1, p.Previous_Date.month, p.Previous_Date.day)
	p.save()
	previous = Empl_Salary_Revisions.objects.filter(Employ_Name=p.Employ_Name).order_by('Effective_From').last()
	p.Previous_Date = previous.Previous_Date if previous != None else p.Employ_Name.Joining_Date if p.Employ_Name.Joining_Date != None else None
	if not p.Next_Revision_Date:
		dt = p.Effective_From
		p.Next_Revision_Date = date(dt.year+1, dt.month, dt.day) if p.Revised_Gross != p.Previous_Gross else  None
	p.save()
	p = Empl_Salary_Revisions.objects.filter(Employ_Name=p.Employ_Name).order_by('Effective_From').last()
	empl_sal.Revision_Status = 1
	empl_sal.save()
	if p.Effective_From <= date.today():
		empl_sal.Gross_Salary = p.Revised_Gross
		empl_sal.Basic = p.Revised_Basic
		empl_sal.Effective_From = p.Effective_From
		empl_sal.save()
		empl_sal = Empl_Salaries.objects.filter(Employ_Name=p.Employ_Name).last()
		update_salary_breaking(request, empl_sal.id)
	return 1

def Signup_Form(request):
	if request.method == 'POST':
		# return HttpResponse('hi')
		form1 = SignUpForm(request.POST, prefix='signup')
		form2 = AccountForm(request.POST, request.FILES, prefix='account')
		if form1.is_valid() * form2.is_valid():
			user = form1.save(commit=False)
			acnt = form2.save(commit=False)
			user.is_active = False
			user.save()
			acnt.save()
			#Asiigning User to Customise Model Account
			usr = Account.objects.get(id=acnt.id)
			usr.user = user
			usr.save()
			try:
				permissions = Permissions.objects.get(user=user)
			except Permissions.DoesNotExist:
				permissions = Permissions.objects.create(user=user)
			username = form1.cleaned_data.get('username')
			raw_password = form1.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			messages.success(request, 'Your Account Has Been Created. Please Contact Admin to Get Activate')
			if request.user.username:
				return redirect('home')
			else:
				return redirect('login')
		else:
			return render(request, 'registration/Signup.html', {'form1': form1, 'form2': form2})
			# return HttpResponse(form1.errors.values())
			# return HttpResponse('<h4>Data You Have Submitted Invalid, Might You Have Missed Some Fields, Go Back and Fill Properle and Submit Again</h4>')
	else:
		form1 = SignUpForm(prefix='signup')
		form2 = AccountForm(prefix='account')
		return render(request, 'registration/Signup.html', {'form1': form1, 'form2': form2})


@login_required
def Manage_User(request, proj):
	pdata = projectname(request, proj)
	# fields = [field.name for field in Permissions._meta.get_fields()][2:] #exclude id and user and get balance fields
	perm = []
	users = Account.objects.filter(user__isnull=False,ds=1)
	for x in users:
		pm = []
		try:
			p = Permissions.objects.get(user=x.user)				
			if p.Admin == True:
				pm.append('Admin')
			if p.Main_Dashboard == True:
				pm.append('Main_Dashboard')
			if p.Proposals_Dashboard == True:
				pm.append('Proposals_Dashboard')
			if p.Expenses_Dashboard == True:
				pm.append('Expenses_Dashboard')
			if p.Create == True:
				pm.append('Create')
			if p.Edit == True:
				pm.append('Edit')
			if p.Delete == True:
				pm.append('Delete')
		except Permissions.DoesNotExist:
			pm = None

		perm.append(pm)
	data = zip(users, perm)
	return render(request, 'registration/ManageUsers.html', {'data':data, 'pdata':pdata})

@login_required
def Edit_Permissions(request, proj, fnc, var):
	pdata = projectname(request, proj)
	acnt = get_object_or_404(Account, id=var)
	user = get_object_or_404(User, username=acnt.user.username)
	data = get_object_or_404(Permissions, user=acnt.user)
	if fnc == 'edit':
		if request.method == 'POST':
			form = PermissionsForm(request.POST, instance=data)
			if form.is_valid():
				p = form.save()
				user = User.objects.get(username=acnt.user.username)
				user.is_active = True
				user.save()
				messages.success(request, 'User Permissions Has Been Updated')
				return redirect('/%s/userslist/'%pdata['pj'])
			else:
				return render(request, 'registration/EditPermissions.html', {'form':form, 'pdata':pdata})
		else:
			form = PermissionsForm(instance=data)
			return render(request, 'registration/EditPermissions.html', {'form':form, 'pdata':pdata})
	elif fnc == 'editaccount':
		if request.method == 'POST':
			# form1 = SignUpEditForm(request.POST, instance=user)
			form2 = AccountForm(request.POST, request.FILES, instance=acnt)
			if form2.is_valid():
				# user = form1.save()
				acnt = form2.save()
				messages.success(request, 'Account Has Been Updated')
				return redirect('/%s/userslist/'%pdata['pj'])
			else:
				return render(request, 'registration/EditAccount.html', {'form1':form1, 'form2':form2})
		else:
			form1 = SignUpForm(instance=user)
			form2 = AccountForm(instance=acnt)
			return render(request, 'registration/EditAccount.html', {'form1':form1, 'form2':form2})
	elif fnc == 'delete':
		acnt.Upload_Photo.delete(save=True)
		acnt.delete()
		user.delete()
		return redirect('/%s/userslist/'%pdata['pj'])

@login_required
def Employes_Form(request, proj, fnc, eid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmployesForm1(request.POST, request.FILES, instance=get_object_or_404(Account, id=eid))
			if form.is_valid():
				p= form.save()
				if p.Status == 0:
					p.ds = 0
					p.save()
				messages.success(request, "Employee Details Has Been Updated successfully")
				return redirect('/%s/employeslist/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/employeslist/'%pdata['pj'])
		else:
			form = EmployesForm1(instance=get_object_or_404(Account, id=eid))
			return render(request, 'registration/EmployesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		emp = Account.objects.get(id=eid)
		emp.Upload_Photo.delete(save=True)
		emp.ds = 0
		emp.Status = 0
		emp.save()
		messages.success(request, "Employee Details Has Been Deleted")
		return redirect('/%s/employeslist/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = EmployesForm(request.POST, request.FILES)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save()
				messages.success(request, "Employee Details Has Been Registered successfully")
				return redirect('/%s/employeslist/'%pdata['pj'])
			else:				
				messages.error(request, get_errors(request, form.errors))
				form = EmployesForm(initial=data_copy)
				return render(request, 'registration/EmployesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			if fnc == 'copy':
				form = EmployesForm(instance=get_object_or_404(Account, id=eid))
				return render(request, 'registration/EmployesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
			else:
				form = EmployesForm()
				return render(request, 'registration/EmployesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required
def Employes_Bank_Form(request, proj, fnc, bid, eid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmployesBankForm(request.POST, request.FILES, instance=get_object_or_404(EMP_Bank_Dtls, id=bid))
			if form.is_valid():
				p= form.save()
				messages.success(request, "Employee Bank Details Has Been Updated successfully")
				return redirect('/%s/employeslist/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/employeslist/'%pdata['pj'])
		else:
			form = EmployesBankForm(instance=get_object_or_404(EMP_Bank_Dtls, id=bid))
			return render(request, 'registration/EmployesBankForm.html', {'form': form, 'pdata':pdata})
	elif fnc == 'delete':
		emp = EMP_Bank_Dtls.objects.get(id=bid)
		emp.delete()
		messages.success(request, "Employee Bank Details Has Been Deleted")
		return redirect('/%s/employeslist/'%pdata['pj'])
	else:
		if request.method == 'POST':
			data_copy = request.POST.items()
			if fnc != 'copy':
				form = EmployesBankForm(request.POST, request.FILES)
			else:
				form = EmployesBankForm1(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				if fnc != 'copy':
					p.Employee = Account.objects.get(id=eid)
					p.save()
				messages.success(request, "Employee Bank Details Has Been Registered successfully")
				return redirect('/%s/employeslist/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				form = EmployesBankForm(initial=data_copy)
				return render(request, 'registration/EmployesBankForm.html', {'form': form, 'pdata':pdata})
		else:
			if fnc == 'copy':
				form = EmployesBankForm1(instance=get_object_or_404(EMP_Bank_Dtls, id=bid))
				return render(request, 'registration/EmployesBankForm.html', {'form': form, 'pdata':pdata})
			else:
				form = EmployesBankForm()
				return render(request, 'registration/EmployesBankForm.html', {'form': form, 'pdata':pdata})

@login_required
def Employes_Prsnl_Form(request, proj, fnc, pid, eid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmployesPrsnlForm1(request.POST, request.FILES, instance=get_object_or_404(EMP_More_Dtls, id=pid))
			if form.is_valid():
				p= form.save()
				messages.success(request, "Employee Personal Details Has Been Updated successfully")
				return redirect('/%s/employeslist/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/employeslist/'%pdata['pj'])
		else:
			form = EmployesPrsnlForm1(instance=get_object_or_404(EMP_More_Dtls, id=pid))
			return render(request, 'registration/EmployesPrsnlForm.html', {'form': form, 'pdata':pdata})
	elif fnc == 'delete':
		emp = EMP_More_Dtls.objects.get(id=pid)
		emp.Upload_Aadhaar.delete(save=True), emp.Upload_PAN.delete(save=True), emp.Upload_PAN.delete(save=True)
		emp.delete()
		messages.success(request, "Employee Personal Details Has Been Deleted")
		return redirect('/%s/employeslist/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = EmployesPrsnlForm(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				if fnc != 'copy':
					p.Employee = Account.objects.get(id=eid)
					p.save()
				messages.success(request, "Employee Personal Details Has Been Registered successfully")
				return redirect('/%s/employeslist/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/employeslist/'%pdata['pj'])
		else:
			if fnc == 'copy':
				form = EmployesPrsnlForm(instance=get_object_or_404(EMP_More_Dtls, id=pid))
				return render(request, 'registration/EmployesPrsnlForm.html', {'form': form, 'pdata':pdata})
			else:
				form = EmployesPrsnlForm()
				return render(request, 'registration/EmployesPrsnlForm.html', {'form': form, 'pdata':pdata})

@login_required
def Employes_List(request, proj):
	pdata = projectname(request, proj)
	emp_ofcl = Account.objects.filter(Status=1, ds=1).order_by('Sr_No')
	count = len(emp_ofcl)
	emp_bank, emp_prsnl = [],[]

	for x in emp_ofcl:
		emp_prsnl.append(EMP_More_Dtls.objects.filter(Employee=x).last() or None)
		emp_bank.append(EMP_Bank_Dtls.objects.filter(Employee=x).last() or None)
	data = zip(emp_ofcl, emp_bank, emp_prsnl)
	# print(emp_ofcl, emp_bank, emp_prsnl)
	# return HttpResponse('l')
	return render(request, 'registration/EmployesList.html', {'data':data, 'pdata':pdata, 'count':count})


@login_required
def Employ_Salaries_Form(request, proj, fnc, eid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmploySalariesForm(request.POST, instance=get_object_or_404(Empl_Salaries, id=eid))
			if form.is_valid():
				p= form.save()
				update_salary_breaking(request, p.id)
				messages.success(request, "Employ Salary Details Has Been Updated successfully")
				return redirect('/%s/employsalarieslist/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/employsalarieslist/'%pdata['pj'])
		else:
			form = EmploySalariesForm(instance=get_object_or_404(Empl_Salaries, id=eid))
			return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		sal = Empl_Salaries.objects.get(id=eid)
		sal.delete()
		messages.success(request, "Employ Salary Details Has Been Deleted")
		return redirect('/%s/employsalarieslist/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = EmploySalariesForm(request.POST)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save()
				update_salary_breaking(request, p.id)
				messages.success(request, "Employee Salary Details Has Been Registered successfully")
				return redirect('/%s/employsalarieslist/'%pdata['pj'])
			else:				
				messages.error(request, get_errors(request, form.errors))
				form = EmploySalariesForm(initial=data_copy)
				return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			if fnc == 'copy':
				form = EmploySalariesForm(instance=get_object_or_404(Empl_Salaries, id=eid))
				return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
			else:
				form = EmploySalariesForm()
				return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required
def Empl_Sal_Revision_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmplSalRevisionsForm(request.POST, instance=get_object_or_404(Empl_Salary_Revisions, id=rid))
			if form.is_valid():
				p= form.save(commit=False)
				empl_sal = Empl_Salaries.objects.filter(Employ_Name=p.Employ_Name).last()
				# if not empl_sal:
				# 	messages.error(request,  "Before Revise Salary Please Register His Joining Salary Using Employ Salary Form")
				# 	return redirect('/%s/emplsalrevisions/'%pdata['pj'])
				# if p.Revised_Gross == empl_sal.Gross_Salary and empl_sal.Basic == p.Previous_Basic:
				# 	messages.error(request, "Revised Salary Must Not Be Same As Previous Salary")
				# 	return redirect('/%s/emplsalrevisions/'%pdata['pj'])
				# else:
				# 	p = form.save()
				p = form.save()
				update_sal_revision(request, p)
				messages.success(request, "Employ Salary Revision Details Has Been Updated successfully")
				return redirect('/%s/emplsalrevisions/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/emplsalrevisions/'%pdata['pj'])
		else:
			form = EmplSalRevisionsForm(instance=get_object_or_404(Empl_Salary_Revisions, id=rid))
			return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		sal_rev = Empl_Salary_Revisions.objects.get(id=rid)
		empl = sal_rev.Employ_Name
		pre_basic = sal_rev.Previous_Basic
		pre_gross = sal_rev.Previous_Gross
		pre_date = sal_rev.Previous_Date
		sal_rev.delete()
		sal_rev = Empl_Salary_Revisions.objects.filter(Employ_Name=empl).order_by('Effective_From').last()
		sal = Empl_Salaries.objects.filter(Employ_Name=empl).last()
		if sal:
			sal.Revision_Status = 0 if sal_rev == None else 1
			sal.Gross_Salary = pre_gross
			sal.Basic = pre_basic
			sal.Effective_From = pre_date
			sal.save()
			update_salary_breaking(request, sal.id)

		messages.success(request, "Employ Salary Revision Details Has Been Deleted")
		return redirect('/%s/emplsalrevisions/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = EmplSalRevisionsForm(request.POST)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save(commit=False)
				empl_sal = Empl_Salaries.objects.filter(Employ_Name=p.Employ_Name).last()
				if not empl_sal:
					messages.error(request,  "Before Revise Salary Please Register His Joining Salary Using Employ Salary Form")
					return redirect('/%s/emplsalrevisions/'%pdata['pj'])
				if p.Revised_Gross == empl_sal.Gross_Salary and empl_sal.Basic == p.Previous_Basic:
					messages.error(request, "Revised Salary Must Not Be Same As Previous Salary")
					return redirect('/%s/emplsalrevisions/'%pdata['pj'])
				else:
					p = form.save()
				p.Previous_Gross = empl_sal.Gross_Salary
				p.Previous_Basic = empl_sal.Basic
				p.Previous_Date = empl_sal.Effective_From
				p.save()
				update_sal_revision(request, p)
				messages.success(request, "Employee Salary Has Been Revised successfully")
				return redirect('/%s/emplsalrevisions/'%pdata['pj'])
			else:				
				messages.error(request, get_errors(request, form.errors))
				form = EmplSalRevisionsForm(initial=data_copy)
				return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'pdata':pdata})
		else:
			if fnc == 'copy':
				form = EmplSalRevisionsForm(instance=get_object_or_404(Empl_Salary_Revisions, id=rid))
				return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
			else:
				form = EmplSalRevisionsForm()
				return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required
def Employ_Salaries(request, proj):
	pdata = projectname(request, proj)
	sal = Empl_Salaries.objects.filter(Status=1).order_by('Employ_Name__Sr_No')
	total_sal = sum(sal.values_list('Gross_Salary', flat=True)) or 0
	count = len(sal)
	sal_rev = []
	for x in sal:
		rev = Empl_Salary_Revisions.objects.filter(Employ_Name=x.Employ_Name).filter(Employ_Name__Status=1).order_by('Effective_From').last()
		if rev:
			if rev.Effective_From <= date.today() and rev.Revised_Gross > x.Gross_Salary:
				x.Gross_Salary = p.Revised_Gross
				x.Basic = p.Revised_Basic
				x.Effective_From = p.Effective_From
				x.save()
				update_salary_breaking(request, x.id)
		sal_rev.append(rev)
	data = zip(sal, sal_rev)
	return render(request, 'attendance/EmploySalaries.html', {'data':data, 'pdata':pdata, 'count':count, 'total_sal':total_sal})

@login_required
def Empl_Sal_Revision(request, proj):
	pdata = projectname(request, proj)
	table = Empl_Salary_Revisions.objects.filter(Employ_Name__Status=1).order_by('-Effective_From', 'Employ_Name__Sr_No')
	return render(request, 'attendance/EmplSalRevisions.html', {'pdata':pdata, 'table':table})