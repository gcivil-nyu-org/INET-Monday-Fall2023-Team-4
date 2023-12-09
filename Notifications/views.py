from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.views import View
from django.db.models import Q
from .models import Notification
from Notifications.models import TransferOwnershipNotif, BookClubUpdatesNotif
from datetime import date


# Create your views here.
class NotificationListView(View):
    model = Notification

    def get(self, request):
        object_list = Notification.objects.filter(
            Q(
                transferownershipnotif__new_owner=self.request.user,
                transferownershipnotif__status="pending",
            )
            | Q(
                transferownershipnotif__original_owner=self.request.user,
                transferownershipnotif__status="declined",
            )
            | Q(bookclubupdatesnotif__receiving_user=self.request.user)
        )

        for n in object_list:
            n.is_read = True
            n.save()
        return render(
            request, "Notifications/notifications.html", {"notifs": object_list}
        )

    def post(self, request, *args, **kwargs):
        notif_type = request.POST.get("notif_type")
        if notif_type == "transfer":
            req_status = request.POST.get("status")
            transferRequestNotif = TransferOwnershipNotif.objects.get(
                id=request.POST["id"]
            )
            if req_status:
                if req_status == "Accept":
                    new_owner = transferRequestNotif.new_owner
                    book_club = transferRequestNotif.book_club
                    if new_owner not in book_club.members.all():
                        book_club.members.add(new_owner)
                    transferRequestNotif.book_club.admin = new_owner
                    transferRequestNotif.status = "accepted"
                    updateNotif = BookClubUpdatesNotif(
                        safe_to_delete=True,
                        date_created=date.today(),
                        receiving_user=request.user,
                        book_club=book_club,
                        fields_changed="new admin",
                    )
                    updateNotif.save()
                else:
                    transferRequestNotif.status = "declined"
                    transferRequestNotif.is_read = False
                transferRequestNotif.safe_to_delete = True
                transferRequestNotif.save()
            else:
                transferRequestNotif.delete()
        else:
            print(request.POST)
            updateNotif = BookClubUpdatesNotif.objects.get(id=request.POST["id"])
            updateNotif.delete()
        return HttpResponseRedirect("#")
