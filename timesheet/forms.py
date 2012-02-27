from django import forms
from models import *

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = ('billed', 'user', 'timesheet')
