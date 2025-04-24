from django import forms
import json

class SoundProfileForm(forms.Form):
    name = forms.CharField(max_length=100)
    bass = forms.IntegerField(min_value=0, max_value=100)
    mid = forms.IntegerField(min_value=0, max_value=100)
    treble = forms.IntegerField(min_value=0, max_value=100)
    environment = forms.CharField(max_length=100, required=False)