from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.validators import RegexValidator
# from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name','class': 'form-control'}))
    last_name = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name','class': 'form-control'}))
    username = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username','class': 'form-control'}))
    email = forms.EmailField(required=True, label='Email', widget=forms.TextInput(attrs={'placeholder': 'email','class': 'form-control'}))
    password1 = forms.CharField(max_length=20, required=True, label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password','class': 'form-control'}))
    password2 = forms.CharField(max_length=20, required=True, label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter Password','class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
    def clean_email(self):  
        email = self.cleaned_data['email'].lower()  
        new = User.objects.filter(email=email)  
        #if new.count():
        #    raise forms.ValidationError("Email Already Exist")  
        #if not validate_email(email):
        #    raise forms.ValidationError("Incorrect email format!") 
        return email  
        
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password.isnumeric():
            raise forms.ValidationError("Password cannot only contain numbers")
        elif password.isalpha():
            raise forms.ValidationError("Password cannot only contain characters")
        else:
            return password

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True) # TODO: send confirmation email to change?

    class Meta:
        model = User
        fields = ['username', 'email']			

class ValidateForm(forms.Form):
	alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
	code = forms.CharField(max_length=10, validators=[alphanumeric])
	
	def clean_code(self):
		code = self.cleaned_data.get('code')
		if code.isalnum():
			return code
		raise forms.ValidationError("Code can only be alphanumeric")
