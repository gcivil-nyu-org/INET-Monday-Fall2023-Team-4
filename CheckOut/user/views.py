from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserRegisterForm, ValidateForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.urls import reverse_lazy
from smtplib import SMTP, SMTPException
import time
import random,string

from .forms import UserRegisterForm, UpdateUserForm
from django.views import View

    
def index(request):
	return render(request, 'user/index.html', {'title':'index'})

def register(request):
	if request.method == 'POST':
		if 'signup' in request.POST:
			form = UserRegisterForm(request.POST)
			request.session['register_form'] = request.POST
			if form.is_valid():
				vcode = ''.join(random.choices(string.ascii_letters, k=5))
				email = form.cleaned_data.get('email');
				print(f'vcode: {vcode}')
				request.session['verification_code'] = { 'code': vcode , 'ttl' : (time.time() + 300)}
				subject, from_email,message = 'Verify Your Email', 'test@gmail.com', f'This is your verification code: {vcode}'
				try:
					send_mail(subject,message,from_email,[email],fail_silently = False,)
					context = {
						'form' : form,
						'title' : 'validate code',
						'verify_code': True,
					}
					return render(request,'user/register.html',context)
				except SMTPException as e:
					print(e)
					context = {
						'form' : form,
						'title' : 'validate code',
						'verify_code': True,
						'email_send_failed' : True
					}
					return render(request,'user/register.html',context)
		elif 'verify' in request.POST:
			print('Verify stuff')
			validate_form = ValidateForm(request.POST)
			print(request.POST)
			if validate_form.is_valid():
				code = validate_form.cleaned_data.get('code')
				validation_token = request.session.get('verification_code')
				print(f'{validation_token}\n Time Now: {time.time()}')
				if validation_token and validation_token['ttl'] > time.time():
					if code == validation_token['code'] :
						post_req = request.session.pop('register_form')
						form = UserRegisterForm(post_req)
						form.save()
						username = form.cleaned_data.get('username')
						email = form.cleaned_data.get('email')
						password = form.cleaned_data.get('password1')
							
						user = authenticate(username=username,password=password)
						login(request,user)
						messages.success(request, f'Your account has been created ! You are now able to log in')
						del request.session['verification_code']
						return redirect('users:index')
					else:
						context = {
							'title' : 'validate code',
							'verify_code': True,
							'validate_failed': True,
							'error_text': 'Incorrect Validation Code, make sure you entered in the right code.'
						}
						return render(request,'user/register.html',context)
				else:
					context = {
							'title' : 'validate code',
							'verify_code': True,
							'validate_failed': True,
							'error_text': 'The verification code has expired.'
					}
					return render(request,'user/register.html',context)
			else:
				print("Failed validation")
			
	else:
		form = UserRegisterForm()
	return render(request, 'user/register.html', {'form': form, 'title':'register here'})

def Login(request):
	if request.method == 'POST':

		# TODO: use AuthenticationForm

		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username = username, password = password)
		if user is not None:
			form = login(request, user)
			messages.success(request, f' welcome {user.username} !!')
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
            return redirect(to='users:user_profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        
    return render(request, 'user/profile.html', {'user_form': user_form})

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'user/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users:index')