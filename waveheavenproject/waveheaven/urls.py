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
    hearing_test,
    save_equalizer_settings,
    equalizer_view,
)

from profiles import views

from profiles.views import (
    user_profile,
    user_statistics
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
      
    # Rutas de función Sound Profile
    path('sound_profiles/', views.profiles_page, name='profiles_page'),
    path('create_profile/', views.create_profile, name='create_profile'),
    path('edit_profile/<int:profile_index>/', views.edit_profile, name='edit_profile'), 
    path('list_profiles/', views.list_profiles, name='list_profiles'),
    path('delete_profile/<int:profile_index>/', views.delete_profile, name='delete_profile'),
    path('apply_profile/<int:profile_id>/', views.apply_profile, name='apply_profile'),
    path('statistics/', user_statistics, name='user_statistics'),
    path('save_equalizer_settings/', save_equalizer_settings, name='save_equalizer_settings'),
    path("profile/", user_profile, name="user_profile"),
    path('apply_profile_by_name/<str:profile_name>/', views.apply_profile_by_name, name='apply_profile_by_name'),

    
]