from django import forms


class JoinClubForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    bookclub_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
