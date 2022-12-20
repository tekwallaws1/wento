from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Projects.basedata import projectname, permissions
from json import dumps
from datetime import date, datetime, timedelta
from Debits.models import Expenses 
from .forms import * 

na_message = '<h3>You do not have authorisation to access this page. Get permissions to get this page. <br>Go back or select another page</h3>'


def get_errors(request, formerrors):
	x = 'Errors: '
	for field, errors in formerrors.items():
			x = x + ('{}'.format(','.join(errors))) + ' '
	return x

def update_salary_breaking(request, sid):
	p = Empl_Salaries.objects.get(id=sid)
	if p.Basic and p.Basic <= 0:
		if p.ESI_Amount and p.ESI_Eligibility == 1:
			p.ESI_Amount = p.Basic*0.0075 
		else:
			p.ESI_Amount = 0
		if p.PF_Amount:	
			pf_per = 0.12 if p.Is_Providing_PF_Employer_Share == True else 0.24
			p.PF_Amount = p.Basic*pf_per if p.PF_Eligibility == True else 0
		else:
			p.PF_Amount = 0

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
	else:
		p.Other_Allowances = p.Net_Salary = p.Gross_Salary
		p.ESI_Amount = p.PF_Amount = 0
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
		form2 = AccountForm1(request.POST, request.FILES, prefix='account')
		if form1.is_valid() * form2.is_valid():
			user = form1.save(commit=False)
			acnt = form2.save(commit=False)
			# user.is_active = False
			user.is_active = True #Customised
			user.save()
			acnt.save()
			#Asiigning User to Customise Model Account
			usr = Account.objects.get(id=acnt.id)
			usr.user = user
			usr.RC.add(*CompanyDetails.objects.filter(Status=1, ds=1))
			usr.save()
			user = Account.objects.get(id=acnt.id)
			try:
				permissions = Page_Permissions.objects.get(user=user)
			except Page_Permissions.DoesNotExist:
				permissions = Page_Permissions.objects.create(user=user)

			#Costomised
			# username = form1.cleaned_data.get('username')
			# raw_password = form1.cleaned_data.get('password1')
			# user = authenticate(username=username, password=raw_password)
			# login(request, user)
			messages.success(request, 'Account Has Been Created. Please Contact Admin to Get Activate Permissions')
			return redirect('home')
			# if request.user.username:
			# 	return redirect('home')
			# else:
			# 	return redirect('login')
		else:
			return render(request, 'registration/Signup.html', {'form1': form1, 'form2': form2})
			# return HttpResponse(form1.errors.values())
			# return HttpResponse('<h4>Data You Have Submitted Invalid, Might You Have Missed Some Fields, Go Back and Fill Properle and Submit Again</h4>')
	else:
		form1 = SignUpForm(prefix='signup')
		form2 = AccountForm1(prefix='account')
		return render(request, 'registration/Signup.html', {'form1': form1, 'form2': form2})

def Signup_Form1(request, firm, proj, aid):
	pdata = projectname(request, proj)
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = True #Customised
			user.save()
			usr = Account.objects.get(id=aid)
			usr.user = user
			usr.RC.add(*CompanyDetails.objects.filter(Status=1, ds=1))
			usr.save()
			messages.success(request, 'Credentials for the selected employ has been generated')
			return redirect('/'+str(firm)+'/'+str(pdata['pj'])+'/employeslist/active/')
		else:
			return render(request, 'registration/Signup1.html', {'form': form, 'firm':firm, 'pdata':pdata})
	else:
		form = SignUpForm()
		return render(request, 'registration/Signup1.html', {'form': form, 'firm':firm, 'pdata':pdata})



@login_required
def Manage_User(request, firm, proj):
	# for x in Projects.objects.all():
	# 	for p in Pages.objects.filter(Related_Project=Projects.objects.all()[0]):
	# 		if p.Page not in Pages.objects.filter(Related_Project=x).values_list('Page', flat=True):
	# 			cretae = Pages.objects.create(Page=p.Page, Related_Project=x)
	# 			cretae.Mode.add(*(p.Mode.all()))
	# 			cretae.RC.add(*(CompanyDetails.objects.all()))
	# return HttpResponse('k')
	# if permissions(request, 'Manage Users', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	# fields = [field.name for field in Permissions._meta.get_fields()][2:] #exclude id and user and get balance fields
	perm_v, perm_e= [], []
	users = Account.objects.filter(RC__Short_Name=firm, user__isnull=False, ds=1, Status=1)
	view_perm = Pages.objects.filter(Mode__Mode='View')
	edit_perm = Pages.objects.filter(Mode__Mode='Edit')
	for x in users:
		p = Page_Permissions.objects.filter(RC__Short_Name=firm, user=x).last()
		pr = []
		pv_all = pe_all = 0, 0
		if p and p.View_Permissions.all():
			if len(p.View_Permissions.all()) == len(view_perm):
				perm_v.append('all')
			else:
				for k in p.View_Permissions.all():
					pr.append(k)
				perm_v.append(pr)
		else:
			perm_v.append(None) 

		pr = []
		if p and p.Edit_Permissions.all():
			if len(p.Edit_Permissions.all()) == len(edit_perm):
				perm_e.append('all')
			else:
				for k in p.Edit_Permissions.all():
					pr.append(k)
				perm_e.append(pr)
		else:
			perm_e.append(None)

	data = zip(users, perm_v, perm_e)
	return render(request, 'registration/ManageUsers.html', {'data':data, 'firm':firm, 'pdata':pdata})

@login_required
def Edit_User(request, firm, proj, fnc, var):
	if permissions(request, 'Manage Users', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	acnt = get_object_or_404(Account, id=var)
	user = get_object_or_404(User, username=acnt.user.username)
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/userslist/'
	if fnc == 'edit' or fnc == 'activate':
		if request.method == 'POST':
			# form1 = SignUpEditForm(request.POST, instance=user)
			form2 = AccountForm(request.POST, request.FILES, instance=acnt)
			if form2.is_valid():
				acnt = form2.save()
				if fnc == 'activate':
					user = User.objects.get(username=acnt.user.username)
					user.is_active = True
					user.save()
				messages.success(request, 'Account Has Been Updated')
				return redirect(url)
			else:
				return render(request, 'registration/EditAccount.html', {'form1':form1, 'form2':form2, 'firm':firm, 'pdata':pdata})
		else:
			form1 = SignUpForm(instance=user)
			form2 = AccountForm(instance=acnt)
			return render(request, 'registration/EditAccount.html', {'form1':form1, 'form2':form2, 'firm':firm, 'pdata':pdata})
	elif fnc == 'delete':
		pre = []
		acnt.Upload_Photo.delete(save=True)
		acnt.ds, acnt.Status = 0, 0
		acnt.save()
		user.is_active = 0
		user.save()
		return redirect(url)

@login_required
def Employes_Form(request, firm, proj, fnc, eid):
	if permissions(request, 'Employs Details', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/employeslist/active/'
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmployesForm1(request.POST, request.FILES, instance=get_object_or_404(Account, id=eid))
			if form.is_valid():
				p= form.save()
				p.RC.add(CompanyDetails.objects.filter(Short_Name=firm).last())
				p.save()
				if p.Status == 0:
					p.ds = 0
					p.save()
				else:
					p.ds = 1
					p.save()
				messages.success(request, "Employee Details Has Been Updated successfully")
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect(url)
		else:
			form = EmployesForm1(instance=get_object_or_404(Account, id=eid))
			form.fields["Related_Project"].queryset = Projects.objects.filter(ds=1, Status='Active', RC__Short_Name=firm)
			return render(request, 'registration/EmployesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		emp = Account.objects.get(id=eid)
		emp.Upload_Photo.delete(save=True)
		emp.ds = 0
		emp.Status = 0
		emp.save()
		Empl_Salaries.objects.filter(Employ_Name=emp, Employ_Name__RC__Short_Name=firm).update(Status=0)
		messages.success(request, "Employee Details Has Been Deleted")
		return redirect(url)
	else:
		if request.method == 'POST':
			form = EmployesForm(request.POST, request.FILES)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save()
				p.RC.add(CompanyDetails.objects.filter(Short_Name=firm).last())
				p.save()
				messages.success(request, "Employee Details Has Been Registered successfully")
				return redirect(url)
			else:				
				messages.error(request, get_errors(request, form.errors))
				form = EmployesForm(initial=data_copy)
				form.fields["Related_Project"].queryset = Projects.objects.filter(ds=1, Status='Active', RC__Short_Name=firm)
				return render(request, 'registration/EmployesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
		else:
			if fnc == 'copy':
				form = EmployesForm(instance=get_object_or_404(Account, id=eid))
				form.fields["Related_Project"].queryset = Projects.objects.filter(ds=1, Status='Active', RC__Short_Name=firm)
				return render(request, 'registration/EmployesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
			else:
				form = EmployesForm()
				form.fields["Related_Project"].queryset = Projects.objects.filter(ds=1, Status='Active', RC__Short_Name=firm)
				return render(request, 'registration/EmployesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})

@login_required
def Employes_Bank_Form(request, firm, proj, fnc, bid, eid):
	if permissions(request, 'Employs Details', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/employeslist/active/'
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmployesBankForm(request.POST, request.FILES, instance=get_object_or_404(EMP_Bank_Dtls, id=bid))
			if form.is_valid():
				p= form.save()
				messages.success(request, "Employee Bank Details Has Been Updated successfully")
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect(url)
		else:
			form = EmployesBankForm(instance=get_object_or_404(EMP_Bank_Dtls, id=bid))
			return render(request, 'registration/EmployesBankForm.html', {'form': form, 'firm':firm, 'pdata':pdata})
	elif fnc == 'delete':
		emp = EMP_Bank_Dtls.objects.get(id=bid)
		emp.delete()
		messages.success(request, "Employee Bank Details Has Been Deleted")
		return redirect(url)
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
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				form = EmployesBankForm(initial=data_copy)
				return render(request, 'registration/EmployesBankForm.html', {'form': form, 'firm':firm, 'pdata':pdata})
		else:
			if fnc == 'copy':
				form = EmployesBankForm1(instance=get_object_or_404(EMP_Bank_Dtls, id=bid))
				return render(request, 'registration/EmployesBankForm.html', {'form': form, 'firm':firm, 'pdata':pdata})
			else:
				form = EmployesBankForm()
				return render(request, 'registration/EmployesBankForm.html', {'form': form, 'firm':firm, 'pdata':pdata})

@login_required
def Employes_Prsnl_Form(request, firm, proj, fnc, pid, eid):
	if permissions(request, 'Employs Details', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/employeslist/active/'
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmployesPrsnlForm1(request.POST, request.FILES, instance=get_object_or_404(EMP_More_Dtls, id=pid))
			if form.is_valid():
				p= form.save()
				messages.success(request, "Employee Personal Details Has Been Updated successfully")
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect(url)
		else:
			form = EmployesPrsnlForm1(instance=get_object_or_404(EMP_More_Dtls, id=pid))
			return render(request, 'registration/EmployesPrsnlForm.html', {'form': form, 'firm':firm, 'pdata':pdata})
	elif fnc == 'delete':
		emp = EMP_More_Dtls.objects.get(id=pid)
		emp.Upload_Aadhaar.delete(save=True), emp.Upload_PAN.delete(save=True), emp.Upload_PAN.delete(save=True)
		emp.delete()
		messages.success(request, "Employee Personal Details Has Been Deleted")
		return redirect(url)
	else:
		if request.method == 'POST':
			form = EmployesPrsnlForm(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				if fnc != 'copy':
					p.Employee = Account.objects.get(id=eid)
					p.save()
				messages.success(request, "Employee Personal Details Has Been Registered successfully")
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect(url)
		else:
			if fnc == 'copy':
				form = EmployesPrsnlForm(instance=get_object_or_404(EMP_More_Dtls, id=pid))
				return render(request, 'registration/EmployesPrsnlForm.html', {'form': form, 'firm':firm, 'pdata':pdata})
			else:
				form = EmployesPrsnlForm()
				return render(request, 'registration/EmployesPrsnlForm.html', {'form': form, 'firm':firm, 'pdata':pdata})

@login_required
def Employes_List(request, firm, proj, status):
	if permissions(request, 'Employs Details', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	if status == 'active':
		emp_ofcl = Account.objects.filter(RC__Short_Name=firm, Status=1, ds=1).order_by('Sr_No')
	else:
		emp_ofcl = Account.objects.filter(RC__Short_Name=firm, Status=0).order_by('Sr_No')
		
	count = len(emp_ofcl)
	emp_bank, emp_prsnl = [],[]

	for x in emp_ofcl:
		emp_prsnl.append(EMP_More_Dtls.objects.filter(Employee=x).last() or None)
		emp_bank.append(EMP_Bank_Dtls.objects.filter(Employee=x).last() or None)
	data = zip(emp_ofcl, emp_bank, emp_prsnl)
	# print(emp_ofcl, emp_bank, emp_prsnl)
	# return HttpResponse('l')
	return render(request, 'registration/EmployesList.html', {'data':data, 'firm':firm, 'pdata':pdata, 'count':count, 'status':status})


@login_required
def Employ_Salaries_Form(request, firm, proj, fnc, eid):
	if permissions(request, 'Salaries Master Data', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/employsalarieslist/active/'
	if fnc == 'edit':
		if request.method == 'POST':
			form = EmploySalariesForm(request.POST, instance=get_object_or_404(Empl_Salaries, id=eid))
			if form.is_valid():
				p= form.save()
				update_salary_breaking(request, p.id)
				messages.success(request, "Employ Salary Details Has Been Updated successfully")
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect(url)
		else:
			form = EmploySalariesForm(instance=get_object_or_404(Empl_Salaries, id=eid))
			form.fields["Employ_Name"].queryset = Account.objects.filter(ds=1, Status=1, RC__Short_Name=firm)
			return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		sal = Empl_Salaries.objects.get(id=eid)
		sal.delete()
		messages.success(request, "Employ Salary Details Has Been Deleted")
		return redirect(url)
	else:
		if request.method == 'POST':
			form = EmploySalariesForm(request.POST)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save()
				update_salary_breaking(request, p.id)
				messages.success(request, "Employee Salary Details Has Been Registered successfully")
				return redirect(url)
			else:				
				messages.error(request, get_errors(request, form.errors))
				form = EmploySalariesForm(initial=data_copy)
				return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
		else:
			if fnc == 'copy':
				form = EmploySalariesForm(instance=get_object_or_404(Empl_Salaries, id=eid))
				form.fields["Employ_Name"].queryset = Account.objects.filter(ds=1, Status=1, RC__Short_Name=firm)
				return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
			else:
				form = EmploySalariesForm()
				form.fields["Employ_Name"].queryset = Account.objects.filter(ds=1, Status=1, RC__Short_Name=firm)
				return render(request, 'attendance/EmploySalariesForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})

@login_required
def Empl_Sal_Revision_Form(request, firm, proj, fnc, rid):
	if permissions(request, 'Salary Revisions', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/emplsalrevisions/'
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
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect(url)
		else:
			form = EmplSalRevisionsForm(instance=get_object_or_404(Empl_Salary_Revisions, id=rid))
			form.fields["Employ_Name"].queryset = Account.objects.filter(ds=1, Status=1, RC__Short_Name=firm)
			return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
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
		return redirect(url)
	else:
		if request.method == 'POST':
			form = EmplSalRevisionsForm(request.POST)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save(commit=False)
				empl_sal = Empl_Salaries.objects.filter(Employ_Name=p.Employ_Name).last()
				if not empl_sal:
					messages.error(request,  "Before Revise Salary Please Register His Joining Salary Using Employ Salary Form")
					return redirect(url)
				if p.Revised_Gross == empl_sal.Gross_Salary and empl_sal.Basic == p.Previous_Basic:
					messages.error(request, "Revised Salary Must Not Be Same As Previous Salary")
					return redirect(url)
				else:
					p = form.save()
				p.Previous_Gross = empl_sal.Gross_Salary
				p.Previous_Basic = empl_sal.Basic
				p.Previous_Date = empl_sal.Effective_From
				p.save()
				update_sal_revision(request, p)
				messages.success(request, "Employee Salary Has Been Revised successfully")
				return redirect(url)
			else:				
				messages.error(request, get_errors(request, form.errors))
				form = EmplSalRevisionsForm(initial=data_copy)
				form.fields["Employ_Name"].queryset = Account.objects.filter(ds=1, Status=1, RC__Short_Name=firm)
				return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata})
		else:
			if fnc == 'copy':
				form = EmplSalRevisionsForm(instance=get_object_or_404(Empl_Salary_Revisions, id=rid))
				form.fields["Employ_Name"].queryset = Account.objects.filter(ds=1, Status=1, RC__Short_Name=firm)
				return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})
			else:
				form = EmplSalRevisionsForm()
				form.fields["Employ_Name"].queryset = Account.objects.filter(ds=1, Status=1, RC__Short_Name=firm)
				return render(request, 'attendance/EmplSalRevisionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'fnc':fnc})

@login_required
def Employ_Salaries(request, firm, proj, mode):
	if permissions(request, 'Salaries Master Data', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	sal = Empl_Salaries.objects.filter(Employ_Name__RC__Short_Name=firm, Status=1).order_by('Employ_Name__Sr_No') if mode == 'active' else Empl_Salaries.objects.filter(Employ_Name__RC__Short_Name=firm, Status=0).order_by('Employ_Name__Sr_No')
	total_sal = sum(sal.values_list('Gross_Salary', flat=True)) or 0
	count = len(sal)
	sal_rev = []
	for x in sal:
		rev = Empl_Salary_Revisions.objects.filter(Employ_Name=x.Employ_Name).filter(Employ_Name__Status=1).order_by('Effective_From').last()
		if rev:
			if rev.Effective_From <= date.today() and rev.Revised_Gross > x.Gross_Salary:
				x.Gross_Salary = rev.Revised_Gross
				x.Basic = rev.Revised_Basic
				x.Effective_From = rev.Effective_From
				x.save()
				update_salary_breaking(request, x.id)
		sal_rev.append(rev)
	data = zip(sal, sal_rev)
	return render(request, 'attendance/EmploySalaries.html', {'data':data, 'firm':firm, 'pdata':pdata, 'count':count, 'total_sal':total_sal, 'mode':mode})

@login_required
def Empl_Sal_Revision(request, firm, proj):
	if permissions(request, 'Salary Revisions', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	table = Empl_Salary_Revisions.objects.filter(Employ_Name__RC__Short_Name=firm, Employ_Name__Status=1).order_by('-Effective_From', 'Employ_Name__Sr_No')
	return render(request, 'attendance/EmplSalRevisions.html', {'firm':firm, 'pdata':pdata, 'table':table})


def permissions_updt(request, firm, proj, inst, fnc):
	inst.Given_By = Account.objects.get(user=request.user)
	inst.Date = date.today()
	inst.RC = CompanyDetails.objects.filter(Short_Name=firm).last()
	inst.Related_Project = Projects.objects.filter(Short_Name=proj).last()
	view_perm = Pages.objects.filter(Mode__Mode='View')
	edit_perm = Pages.objects.filter(Mode__Mode='Edit')

	if len(inst.View_Permissions.all()) == len(view_perm) and len(inst.Edit_Permissions.all()) == len(edit_perm):
		inst.Is_Admin = 1
		inst.save()
		return 1
	
	if inst.Is_Admin == 1:
		if firm != 'All':
			projects = Projects.objects.filter(RC__Short_Name=firm, Status='Active', ds=1)
			inst.View_Permissions.add(*view_perm)
			inst.Edit_Permissions.add(*edit_perm)
		else:
			view_perm = Pages.objects.filter(Mode__Mode='Edit')
			edit_perm = Pages.objects.filter(Mode__Mode='Edit')
			inst.View_Permissions.add(*view_perm)
			inst.Edit_Permissions.add(*edit_perm)
	inst.save()

@login_required
def Page_Permissions_Form(request, firm, proj, fnc, eid):
	if permissions(request, 'Manage Users', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	ac = Account.objects.filter(id=eid).last()
	pm = Page_Permissions.objects.filter(RC__Short_Name=firm, user=ac).last()
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/userslist/'
	if pm:
		pid = pm.id
	else:
		pid, fnc = 1, 'create'
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(Page_Permissions, id=pid)
			form = PagePermissionsForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				permissions_updt(request, firm, proj, Page_Permissions.objects.get(id=p.id), fnc)
				messages.success(request, "Permissions Has Been Updated")
				return redirect(url)
			else:
				return render(request, 'registration/PagePermissionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(Page_Permissions, id=pid)
			form = PagePermissionsForm(instance=getdata)
			prm = getdata.View_Permissions.all()
			return render(request, 'registration/PagePermissionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'firm':firm, 'prm':prm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(Page_Permissions, id=rid)
		getdata.delete()
		messages.success(request, "Permissions Has Been Deleted")
		return redirect(url)

	if request.method ==  'POST': #Create
		form = PagePermissionsForm(request.POST, request.FILES) if fnc == 'create' else PagePermissionsFormCopy(request.POST, request.FILES)
		if form.is_valid():
			p = form.save(commit=False)
			pm = Page_Permissions.objects.filter(RC__Short_Name=firm, user=p.user)
			if pm:
				messages.error(request, 'User Already Have Permissions. Edit Permissions Instead of Create New Permissions')
				return redirect(url)
			p = form.save()
			p.user = Account.objects.get(id=eid)
			p.save()
			permissions_updt(request, firm, proj, Page_Permissions.objects.get(id=p.id), fnc)
			messages.success(request, "Permissions Has Been Added")			
			return redirect(url)
		else:
			return render(request, 'registration/PagePermissionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Page_Permissions, id=pid)
			form = PagePermissionsFormCopy(instance=getdata)
			return render(request, 'registration/PagePermissionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'firm':firm})
		else:
			form = PagePermissionsForm()
			prm = Pages.objects.filter(Mode__Mode='View')
			form.fields["RC"].queryset = CompanyDetails.objects.filter(Short_Name=firm, Status=1, ds=1)
			# form.fields["View_Permissions"].queryset = View_Pages.objects.filter(RC__Short_Name=firm, Related_Project__Short_Name=proj)
			# form.fields["Edit_Permissions"].queryset = Edit_Pages.objects.filter(RC__Short_Name=firm, Related_Project__Short_Name=proj)
			return render(request, 'registration/PagePermissionsForm.html', {'form': form, 'firm':firm, 'pdata':pdata, 'firm':firm, 'prm':prm})