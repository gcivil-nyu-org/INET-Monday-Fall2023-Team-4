from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.contrib import messages

from django.views.generic.list import ListView
from django.db.models import Q
from .models import Notification
from django.views.generic.edit import FormMixin

# Create your views here.
class NotificationListView(FormMixin, ListView):
    model = Notification
    paginate_by = 10
    
    def get_queryset(self):
        object_list = Notification.objects.filter(Q(TransferOwnershipNotif__new_owner=self.request.user, TransferOwnershipNotif__status="pending") | Q(TransferOwnershipNotif__original_owner=request.user, TransferOwnershipNotif__status="declined") | Q(BookClubUpdatesNotif__receiving_user=self.request.user))
        
        return object_list
    
    def post(self, request, *args, **kwargs):
        notif_type = request.POST.get("type")
        if notif_type == 'transfer':
            req_status = request.POST.get("status")
            if req_status:
                transferRequestNotif = TransferOwnershipNotif.objects.get(
                    id=request.POST["id"]
                )
                if req_status == "Accept":
                    new_owner = transferRequestNotif.new_owner
                    book_club = get_object_or_404(BookClub, id=request.POST["book_club"])
                    if new_owner not in book_club.members.all():
                        book_club.members.add(new_owner)
                    transferRequestNotif.book_club.admin = new_owner
                    transferRequestNotif.status = "accepted"
                else:
                    transferRequestNotif.status = "declined"
                transferRequestNotif.save()
            else:
                transferRequestNotif.delete()
        else:
            updateNotif = BookClubUpdatesNotif.objects.get(
                    id=request.POST["id"]
                )
            updateNotif.delete()
        return HttpResponseRedirect("#")
    
