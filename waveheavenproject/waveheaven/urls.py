from django.urls import path
from wa.views import (
    home, 
    toggle_microphone, 
    adjust_volume,
    set_sound_category  # Import the function directly
)

urlpatterns = [
    path('', home, name='home'),
    path('api/toggle_microphone/', toggle_microphone, name='toggle_microphone'),
    path('api/adjust_volume/', adjust_volume, name='adjust_volume'),
    path('api/set_sound_category/', set_sound_category, name='set_sound_category'),  # Use the function directly
]