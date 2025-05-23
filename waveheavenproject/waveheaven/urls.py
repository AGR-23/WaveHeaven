from django.contrib import admin
from django.urls import include, path
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
    save_exposure_time,
    record_hearing_risk,
    spotify_login,
    spotify_callback,
    spotify_player,
    spotify_playback,
    spotify_search_playback,
    update_party_settings,
    join_party_session,  
    create_party_session,
    leave_party,
    send_chat_message,
    get_chat_messages,
)

from profiles import views

from profiles.views import (
    user_profile,
    user_statistics,
    age_vs_volume_view
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
    path('save_exposure_time/', save_exposure_time, name='save_exposure_time'),
    path('record_hearing_risk/', record_hearing_risk, name='record_hearing_risk'),
    path('age-vs-volume/', views.age_vs_volume_view, name='age_vs_volume'),
    
    
    # Spotify API
    path('spotify/', spotify_login, name='spotify_login'),
    path('spotify/callback/', spotify_callback, name='spotify_callback'),
    path('spotify/player/', spotify_player, name='spotify_player'),
    path('spotify/playback/', spotify_playback, name='spotify_playback'),
    path('spotify/search/', spotify_search_playback, name='spotify_search_playback'),
    
    # Party Session
    path('party/create/', create_party_session, name='create_party'),
    path('party/join/', join_party_session, name='join_party'),
    path('party/settings/', update_party_settings, name='update_party_settings'),
    path('party/chat/send/', send_chat_message, name='send_chat_message'),
    path('party/chat/<int:party_id>/', get_chat_messages, name='get_chat_messages'),
    path('party/leave/', leave_party, name='leave_party'),
    ]