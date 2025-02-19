from django.urls import path
from wa.views import home, toggle_microphone, adjust_volume  # Asegúrate de que adjust_volume está aquí

urlpatterns = [
    path('', home, name='home'),
    path('api/toggle_microphone/', toggle_microphone, name='toggle_microphone'),
    path('api/adjust_volume/', adjust_volume, name='adjust_volume'),
]