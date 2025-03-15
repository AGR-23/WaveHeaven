from django.contrib import admin
from django.urls import include
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
from profiles import views
from profiles.views import user_statistics

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
    
    # Rutas de función Sound Profile
    path('profiles/', views.list_profiles, name='list_profiles'),
    path('create/', views.create_profile, name='create_profile'),
    path('edit/<int:profile_id>/', views.edit_profile, name='edit_profile'),
    path('apply/<int:profile_id>/', views.apply_profile, name='apply_profile'),
    path('statistics/', user_statistics, name='user_statistics'),
]