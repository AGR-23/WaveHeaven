from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from wa.views import (
    home, 
    toggle_microphone, 
    adjust_volume, 
    set_sound_category, 
    user_register,
    user_dashboard,
    user_login,
    user_logout,
    hearing_test
)

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Página principal
    path('', home, name='home'),

    # Rutas de autenticación
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', user_register, name='register'),

    # API endpoints
    path('api/toggle_microphone/', toggle_microphone, name='toggle_microphone'),
    path('api/adjust_volume/', adjust_volume, name='adjust_volume'),
    path('api/set_sound_category/', set_sound_category, name='set_sound_category'),
    path("dashboard/", user_dashboard, name="dashboard"),
    path("hearing-test/", hearing_test, name="hearing_test"),


]