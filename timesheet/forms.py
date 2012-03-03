from django import forms
from models import Entry, UserProfile
from django.contrib.auth.models import User

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = ('billed', 'user', 'timesheet')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

