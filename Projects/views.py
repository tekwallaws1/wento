from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from .models import *
# from .forms import *
# from .filters import *
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date, datetime, timedelta 
import re
from django.db.models import Sum, Avg, Count
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q
import random 
from django.urls import reverse  
import os
from django.conf import settings
from django.template.loader import get_template
from num2words import num2words 
from UserAccounts.models import *
from .basedata import basedata


# @login_required
def Select_Project(request):
	pdata = basedata(request, None)
	return render(request, 'projects/SelectProject.html', {'pdata':pdata})

@login_required
def Select_Module(request, proj):
	pdata = basedata(request, proj)
	return render(request, 'projects/SelectModule.html', {'pdata':pdata})