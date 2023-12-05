from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.contrib import messages

from django.views.generic.list import ListView
from django.db.models import Q
from .models import Notification

# Create your views here.
class NotificationListView(ListView):
    model = Notification
    paginate_by = 10
    
    def get_queryset(self):
        object_list = Notification.objects.filter(new_owner=self.request.user, status="pending")
