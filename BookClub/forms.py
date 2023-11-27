from django import forms
from django.forms import ModelForm
from .models import BookClub
from user.models import CustomUser


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
    new_admin = forms.ModelChoiceField(
        label="New Admin", queryset=CustomUser.objects.all()
    )

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
        )

        exclude = ["admin"]
