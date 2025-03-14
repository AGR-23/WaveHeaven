from django import forms
import json

class SoundProfileForm(forms.Form):
    name = forms.CharField(max_length=100, label="Nombre del Perfil")
    bass = forms.IntegerField(min_value=0, max_value=100, label="Bajos")
    mid = forms.IntegerField(min_value=0, max_value=100, label="Medios")
    treble = forms.IntegerField(min_value=0, max_value=100, label="Altos")
    environment = forms.CharField(max_length=100, label="Entorno", required=False)