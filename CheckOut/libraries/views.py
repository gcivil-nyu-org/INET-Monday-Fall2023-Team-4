from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.template import loader

# Create your views here.


def index(request):
	template = loader.get_template('libraries/index.html')
	context = {}
	return HttpResponse(template.render(context, request))