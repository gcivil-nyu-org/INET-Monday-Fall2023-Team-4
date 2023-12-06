from django import forms
from django.forms import ModelForm
from .models import BookClub
from user.models import CustomUser
from django.core.exceptions import ValidationError


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
            "currentBookIsbn": "Current Book Isbn",
            "meetingStartTime": "Meeting Start Time",
            "meetingEndTime": "Meeting End Time",
            "meetingDay": "Meeting Day",
        }

    def __init__(self, *args, **kwargs):
        super(BookClubForm, self).__init__(*args, **kwargs)
        self.fields["meetingDay"].required = True
        self.fields["meetingOccurence"].required = True
        self.fields["meetingStartTime"].widget = forms.TimeInput(
            format="%I:%M %p", attrs={"type": "time"}
        )
        self.fields["meetingEndTime"].widget = forms.TimeInput(
            format="%I:%M %p", attrs={"type": "time"}
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
        label="New Admin", queryset=CustomUser.objects.all()
    )

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
            "libraryId",
        )

        exclude = ["admin"]
