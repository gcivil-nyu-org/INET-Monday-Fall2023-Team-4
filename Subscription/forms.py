from django import forms
from BookClub.models import BookClub
from user.models import CustomUser
from Subscription.models import Subscription

from datetime import date


class JoinClubForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    bookclub_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
