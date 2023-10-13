from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.template import loader

# Create your views here.


def login(request):
	template = loader.get_template('login/login.html')
	context = {}
	return HttpResponse(template.render(context, request))
    
	