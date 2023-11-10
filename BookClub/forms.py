from django.forms import ModelForm
from .models import BookClub


class BookClubForm(ModelForm):
    class Meta:
        model = BookClub
        fields = (
            "name",
            "description",
            "currentBook",
            "meetingDay",
            "meetingStartTime",
            "meetingEndTime",
            "meetingOccurence",
        )


class BookClubEditForm(ModelForm):
    class Meta:
        model = BookClub
        fields = (
            "name",
            "description",
            "currentBook",
            "meetingDay",
            "meetingStartTime",
            "meetingEndTime",
            "meetingOccurence",
            "libraryId",
            "admin",
        )
