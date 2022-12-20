from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.forms import Form, ModelForm, DateField, widgets
from django.forms import DateTimeField, DateTimeInput

class SignUpForm(UserCreationForm):
    # first_name      = forms.CharField(max_length=20, required=True, help_text='First Name')
    # last_name       = forms.CharField(max_length=20, required=False, help_text='Last Name')
    # email = forms.EmailField(max_length=254, required=False, widget=forms.TextInput(attrs={'placeholder': 'Ener a Vaild Email Address'}))

    class Meta:
        model = User
        # fields = ('username', 'email', 'password1', 'password2')
        # help_texts = {
        #         'email': ('enter valid email address'),
        # }

        fields = ('username',  'password1', 'password2')
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['email'].widget.attrs['help_text'] = 'css_class' 
        # for _, value in self.fields.items():
        #     pass
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4' 
            })


class AccountForm(forms.ModelForm):    
    class Meta:
        model = Account
        exclude = ['user', 'ds', 'Is_Super_Admin', 'Sr_No']
        widgets = {'Joining_Date': widgets.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class AccountForm1(forms.ModelForm):    
    class Meta:
        model = Account
        exclude = ['user', 'ds', 'Joining_Date', 'Email', 'Status', 'RC', 'Is_Super_Admin', 'Sr_No']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class PermissionsForm(forms.ModelForm):    
    class Meta:
        model = Page_Permissions
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class EmployesForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ['user', 'ds', 'Status', 'RC', 'Sr_No', 'Is_Super_Admin']    
        widgets = {'Joining_Date': widgets.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })
class EmployesForm1(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ['user', 'ds', 'RC', 'Sr_No', 'Is_Super_Admin']
        widgets = {'Joining_Date': widgets.DateInput(attrs={'type': 'date'})}    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class EmployesBankForm(forms.ModelForm):
    class Meta:
        model = EMP_Bank_Dtls
        exclude = ['Status', 'Employee']    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class EmployesBankForm1(forms.ModelForm):
    class Meta:
        model = EMP_Bank_Dtls
        exclude = ['Status']    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class EmployesPrsnlForm(forms.ModelForm):
    class Meta:
        model = EMP_More_Dtls
        exclude = ['Employee']    
        widgets = {'DOB': widgets.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class EmployesPrsnlForm1(forms.ModelForm):
    class Meta:
        model = EMP_More_Dtls
        exclude = ['Employee']    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class EmploySalariesForm(forms.ModelForm):
    class Meta:
        model = Empl_Salaries
        exclude = ['HRA','Other_Allowances','Status', 'PF_Amount','ESI_Amount','Professional_Tax','Revision_Status','Net_Salary']    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

class EmplSalRevisionsForm(forms.ModelForm):
    class Meta:
        model = Empl_Salary_Revisions
        exclude = ['Previous_Date','Previous_Gross','Previous_Basic', 'Status']   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })


class PagePermissionsForm(forms.ModelForm): 
    class Meta:
        model = Page_Permissions
        exclude = ['Given_By', 'user',  'Date', 'Related_Project']

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-4'})

    View_Permissions = forms.ModelMultipleChoiceField(queryset=Pages.objects.filter(Mode__Mode='View').order_by('Category'), widget=forms.CheckboxSelectMultiple, required=False)
    Edit_Permissions = forms.ModelMultipleChoiceField(queryset=Pages.objects.filter(Mode__Mode='Edit').order_by('Category'), widget=forms.CheckboxSelectMultiple, required=False)        
    
    def __init__(self, *args, **kwargs):
      forms.ModelForm.__init__(self, *args, **kwargs)

    # def __init__(self, *args, **kwargs):
    #   firm = kwargs.pop('fm')
    #   if firm:
    #       # super().__init__(*args, **kwargs)   #yu can use this also   
    #       forms.ModelForm.__init__(self, *args, **kwargs)
    #       self.fields['View_Permissions'].queryset = Pages.objects.filter(RC__Short_Name=firm, Mode__Mode='View').order_by('Related_Project')
    #       self.fields['Edit_Permissions'].queryset = Pages.objects.filter(RC__Short_Name=firm, Mode__Mode='Edit').order_by('Related_Project')

    # def __init__(self,  fm=None, *args, **kwargs):
    #   super().__init__(*args, **kwargs)      
    #   # forms.ModelForm.__init__(self, *args, **kwargs)
    #   self.fields['View_Permissions'].queryset =Pages.objects.filter(RC__Short_Name=fm, Mode__Mode='View')

    #   self.fields["Related_Project"].widget = CheckboxSelectMultiple()
    #   self.fields["Related_Project"].queryset = Projects.objects.all()


class PagePermissionsFormCopy(forms.ModelForm): 
    class Meta:
        model = Page_Permissions
        exclude = ['Given_By',  'Date', 'Related_Project']

    View_Permissions = forms.ModelMultipleChoiceField(
        queryset=Pages.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

    View_Permissions = forms.ModelMultipleChoiceField(queryset=Pages.objects.filter(Mode__Mode='View').order_by('Category'), widget=forms.CheckboxSelectMultiple, required=False)
    Edit_Permissions = forms.ModelMultipleChoiceField(queryset=Pages.objects.filter(Mode__Mode='Edit').order_by('Category'), widget=forms.CheckboxSelectMultiple, required=False)        
    
    # def __init__(self, *args, **kwargs):
    #   firm = kwargs.pop('fm')
    #   if firm:
    #       # super().__init__(*args, **kwargs)   #yu can use this also   
    #       forms.ModelForm.__init__(self, *args, **kwargs)
    #       self.fields['View_Permissions'].queryset = Pages.objects.filter(RC__Short_Name=firm, Mode__Mode='View').order_by('Related_Project')
    #       self.fields['Edit_Permissions'].queryset = Pages.objects.filter(RC__Short_Name=firm, Mode__Mode='Edit').order_by('Related_Project')