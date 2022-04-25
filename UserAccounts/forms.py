from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class SignUpForm(UserCreationForm):
    # first_name      = forms.CharField(max_length=20, required=True, help_text='First Name')
    # last_name       = forms.CharField(max_length=20, required=False, help_text='Last Name')
    email = forms.EmailField(max_length=254, required=False, widget=forms.TextInput(attrs={'placeholder': 'Ener a Vaild Email Address'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
                'email': ('enter valid email address'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['email'].widget.attrs['help_text'] = 'css_class' 
        # for _, value in self.fields.items():
        #     pass
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

# class SignUpEditForm(UserCreationForm):
#     first_name      = forms.CharField(max_length=20, required=True, help_text='First Name')
#     last_name       = forms.CharField(max_length=20, required=False, help_text='Last Name')

#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for _, value in self.fields.items():
#             value.widget.attrs['placeholder'] = value.help_text
#         for field in self.fields:
#             self.fields[field].widget.attrs.update({
#                 'class': 'form-control mb-4'
#             })

class AccountForm(forms.ModelForm):    
    class Meta:
        model = Account
        exclude = ['user', 'ds']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })

# class AccountEditForm(forms.ModelForm):    
#     class Meta:
#         model = Account
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for _, value in self.fields.items():
#             value.widget.attrs['placeholder'] = value.help_text
#         for field in self.fields:
#             self.fields[field].widget.attrs.update({
#                 'class': 'form-control mb-4'
#             })

class PermissionsForm(forms.ModelForm):    
    class Meta:
        model = Permissions
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.help_text
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-4'
            })