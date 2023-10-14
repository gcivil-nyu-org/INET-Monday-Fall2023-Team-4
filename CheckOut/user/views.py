from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserRegisterForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.urls import reverse_lazy

from .forms import UserRegisterForm, UpdateUserForm
from django.views import View

    
def index(request):
	return render(request, 'user/index.html', {'title':'index'})

class RegisterView(View):
    form_class = UserRegisterForm
    initial = {'key': 'value'}
    template = 'user/register.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username,password=password)
            login(request, user)
   
            messages.success(request, f'Account created for {username}')

            return redirect(to='/')

        return render(request, self.template, {'form': form})

def Login(request):
	if request.method == 'POST':

		# TODO: use AuthenticationForm

		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username = username, password = password)
		if user is not None:
			form = login(request, user)
			messages.success(request, f' welcome {user.first_name} !!')
			return redirect('users:index')
		else:
			messages.info(request, f'account does not exist plz sign in')
	form = AuthenticationForm()
	return render(request, 'user/login.html', {'form':form, 'title':'log in'})

@login_required

def user_profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='user_profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        
    return render(request, 'user/profile.html', {'user_form': user_form})

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'user/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users:index')