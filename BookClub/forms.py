from django import forms
from django.forms import ModelForm
from .models import BookClub
from user.models import CustomUser
from django.core.exceptions import ValidationError
from Notifications.models import TransferOwnershipNotif


class BookClubVotingForm(forms.Form):
    book1 = forms.CharField(label="book1", max_length=200)
    book2 = forms.CharField(label="book2", max_length=200)
    book3 = forms.CharField(label="book3", max_length=200)


class BookClubForm(ModelForm):
    class Meta:
        model = BookClub
        fields = (
            "name",
            "description",
            "currentBook",
            "currentAuthor",
            "currentBookIsbn",
            "meetingDay",
            "meetingStartTime",
            "meetingEndTime",
            "meetingOccurence",
        )
        labels = {
            "currentBook": "Current Book",
            "currentAuthor": "Current Author",
            "currentBookIsbn": "Current Book ISBN",
            "meetingStartTime": "Meeting Start Time",
            "meetingEndTime": "Meeting End Time",
            "meetingDay": "Meeting Day",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "cols": 50, "rows": 3}
            ),
            "currentBook": forms.TextInput(attrs={"class": "form-control"}),
            "currentAuthor": forms.TextInput(attrs={"class": "form-control"}),
            "currentBookIsbn": forms.TextInput(attrs={"class": "form-control"}),
            "meetingDay": forms.Select(attrs={"class": "form-control"}),
            "meetingOccurence": forms.Select(attrs={"class": "form-control"}),
            "libraryId": forms.Select(attrs={"class": "form-control"}),
            "admin": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(BookClubForm, self).__init__(*args, **kwargs)
        self.fields["meetingDay"].required = True
        self.fields["meetingOccurence"].required = True
        self.fields["meetingStartTime"].widget = forms.TimeInput(
            format="%I:%M %p", attrs={"class": "form-control", "type": "time"}
        )
        self.fields["meetingEndTime"].widget = forms.TimeInput(
            format="%I:%M %p", attrs={"class": "form-control", "type": "time"}
        )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("meetingStartTime")
        end_time = cleaned_data.get("meetingEndTime")

        if start_time and end_time and end_time <= start_time:
            raise ValidationError(
                "Meeting end time must be after the meeting start time."
            )

        return cleaned_data


class BookClubEditForm(ModelForm):
    new_admin = forms.ModelChoiceField(
        label="New Admin",
        queryset=CustomUser.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = BookClub
        fields = [
            "name",
            "description",
            "currentBook",
            "currentAuthor",
            "currentBookIsbn",
            "meetingDay",
            "meetingStartTime",
            "meetingEndTime",
            "meetingOccurence",
            "libraryId",
        ]

        exclude = ["admin"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "cols": 50, "rows": 3}
            ),
            "currentBook": forms.TextInput(attrs={"class": "form-control"}),
            "currentAuthor": forms.TextInput(attrs={"class": "form-control"}),
            "currentBookIsbn": forms.TextInput(attrs={"class": "form-control"}),
            "meetingDay": forms.Select(attrs={"class": "form-control"}),
            "meetingStartTime": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "meetingEndTime": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "meetingOccurence": forms.Select(attrs={"class": "form-control"}),
            "libraryId": forms.Select(attrs={"class": "form-control"}),
            # "new_admin": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Name",
            "description": "Description",
            "currentBook": "Current book pick",
            "currentAuthor": "Current pick's author",
            "currentBookIsbn": "Current pick's ISBN",
            "meetingDay": "Meeting day",
            "meetingStartTime": "Meeting Start Time",
            "meetingEndTime": "Meeting End Time",
            "meetingOccurence": "Meeting Frequency",
            "libraryId": "Library",
        }

    def clean_new_admin(self):
        # each book club should only have one pending request
        new_admin = self.cleaned_data["new_admin"]
        pending_req = TransferOwnershipNotif.objects.filter(
            book_club=self.instance, status="pending"
        )
        error_message = (
            "You have already made a transfer admin request."
            + "Please wait for the previous request to be declined to make a new one."
        )
        if pending_req:
            raise ValidationError(error_message)
        return new_admin
