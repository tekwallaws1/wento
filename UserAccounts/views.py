from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User



from .forms import *

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
				return redirect('/userslist/')
			else:
				return redirect('login')
		else:
			return HttpResponse('<h4>Data You Have Submitted Invalid, Might You Have Missed Some Fields, Go Back and Fill Properle and Submit Again</h4>')
	else:
		form1 = SignUpForm(prefix='signup')
		form2 = AccountForm(prefix='account')
		return render(request, 'registration/Signup.html', {'form1': form1, 'form2': form2})



def Manage_User(request):
	# fields = [field.name for field in Permissions._meta.get_fields()][2:] #exclude id and user and get balance fields
	perm = []
	users = Account.objects.filter(ds=1)
	for x in users:
		if x.user:
			try:
				p = Permissions.objects.get(user=x.user)
				pm = []
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
	return render(request, 'registration/ManageUsers.html', {'data':data})

def Edit_Permissions(request, fnc, var):
	acnt = get_object_or_404(Account, id=var)
	print(acnt.id)
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
				messages.success(request, 'User Permissions Has Been Update')
				return redirect('/userslist/')
			else:
				return HttpResponse('Data You Have Enetered is Something Wrong, Please Go Back and Correct and Submit Again')
		else:
			form = PermissionsForm(instance=data)
			return render(request, 'registration/EditPermissions.html', {'form':form})
	elif fnc == 'editaccount':
		if request.method == 'POST':
			# form1 = SignUpEditForm(request.POST, instance=user)
			form2 = AccountForm(request.POST, request.FILES, instance=acnt)
			if form2.is_valid():
				# user = form1.save()
				acnt = form2.save()
				messages.success(request, 'Account Has Been Updated')
				return redirect('/userslist/')
			else:
				# print(form1.errors)
				# print(form2.errors)
				return HttpResponse('Data You Have Enetered is Something Wrong, Please Go Back and Correct and Submit Again')
		else:
			form1 = SignUpForm(instance=user)
			form2 = AccountForm(instance=acnt)
			return render(request, 'registration/EditAccount.html', {'form1':form1, 'form2':form2})
	elif fnc == 'delete':
		acnt.ds = 0
		acnt.save()
		user.delete()
		return redirect('/userslist/')




