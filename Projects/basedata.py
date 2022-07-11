from UserAccounts.models import Account
from django.contrib.auth.models import User
from .models import Projects

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


		
