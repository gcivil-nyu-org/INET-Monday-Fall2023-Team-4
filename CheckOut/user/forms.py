from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()
	first_name = forms.CharField(max_length = 20)
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']
	def clean_password1(self):
		password = self.cleaned_data.get("password1")
		if password.isnumeric():
			raise forms.ValidationError("Password can not only contain numbers")
		elif password.isalpha():
			raise forms.ValidationError("Password can not only contain characters")
		else:
			return password