from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length = 20, required=True)
    last_name = forms.CharField(max_length = 20, required=True)
    username = forms.CharField(max_length = 20, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(max_length = 20, required=True)
    password2 = forms.CharField(max_length = 20, required=True)
 
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2']
        
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password.isnumeric():
            raise forms.ValidationError("Password cannot only contain numbers")
        elif password.isalpha():
            raise forms.ValidationError("Password cannot only contain characters")
        else:
            return password