from django import forms
from django.forms import ModelForm
from .models import BookClub

class BookClubForm(ModelForm):
    class Meta:
        model = BookClub
        

