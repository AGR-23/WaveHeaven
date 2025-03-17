from django.urls import path
from .views import user_statistics, user_profile
from wa.vies import (
    equalizer_view,
)

urlpatterns = [
    path('statistics/', user_statistics, name='user_statistics'),
    path("profile/", user_profile, name="user_profile"),
    path("equalizer/", equalizer_view, name="equalizer_view"),
]