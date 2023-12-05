from django.db import models
from user.models import CustomUser

# Create your models here.
class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    # receiving_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    class Meta:
        abstract = True
        ordering = ["date_created"]    

class TransferOwnershipNotif(Notification):
    original_owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="old_admin"
    )
    new_owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="new_admin"
    )
    book_club = models.ForeignKey(
        "BookClub.BookClub", on_delete=models.CASCADE, related_name="transferred_book_club"
    )
    status_types = ["accepted", "pending", "declined"]
    status = models.CharField(status_types, max_length=30)


class BookClubUpdatesNotif(Notification):
    receiving_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="receiving_user"
    )
    book_club = models.ForeignKey(
        "BookClub.BookClub", on_delete=models.CASCADE, related_name="updated_book_club"
    )
    fields_changed = models.TextField()
    
