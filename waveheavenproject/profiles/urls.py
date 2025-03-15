from django.urls import path
from .views import user_statistics

urlpatterns = [
    path('statistics/', user_statistics, name='user_statistics'),
]