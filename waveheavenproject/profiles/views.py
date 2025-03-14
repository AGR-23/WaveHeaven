from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from wa.models import UserPreferences
from .forms import SoundProfileForm

@login_required
def apply_profile(request, profile_id):
    # Obtener las preferencias del usuario actual
    user_prefs = get_object_or_404(UserPreferences, user=request.user)
    profiles = user_prefs.get_audio_profiles()

    # Verificar que el índice del perfil sea válido
    if profile_id < 0 or profile_id >= len(profiles):
        return redirect('list_profiles')  # Redirigir si el perfil no existe

    # Aplicar el perfil (aquí puedes agregar la lógica para aplicar los ajustes)
    profile = profiles[profile_id]
    print(f"Aplicando perfil: {profile}")  # Simulación de aplicación

    return redirect('list_profiles')  # Redirigir a la lista de perfil

@login_required
def list_profiles(request):
    # Obtener o crear las preferencias del usuario actual
    user_prefs, created = UserPreferences.objects.get_or_create(user=request.user)
    profiles = user_prefs.get_audio_profiles()  # Obtener los perfiles del usuario
    return render(request, 'profiles.html', {'profiles': profiles})

@login_required
def create_profile(request):
    user_prefs = get_object_or_404(UserPreferences, user=request.user)
    if request.method == 'POST':
        form = SoundProfileForm(request.POST)
        if form.is_valid():
            profiles = user_prefs.get_audio_profiles()
            profiles.append(form.cleaned_data)
            user_prefs.save_audio_profiles(profiles)
            return redirect('list_profiles')
    else:
        form = SoundProfileForm()
    return render(request, 'profiles/create_profile.html', {'form': form})

@login_required
def edit_profile(request, profile_index):
    user_prefs = get_object_or_404(UserPreferences, user=request.user)
    profiles = user_prefs.get_audio_profiles()

    # Verificar que el índice del perfil sea válido
    if profile_index < 0 or profile_index >= len(profiles):
        return redirect('list_profiles')  # Redirigir si el perfil no existe

    profile = profiles[profile_index]

    if request.method == 'POST':
        form = SoundProfileForm(request.POST)
        if form.is_valid():
            profiles[profile_index] = form.cleaned_data
            user_prefs.save_audio_profiles(profiles)
            return redirect('list_profiles')
    else:
        form = SoundProfileForm(initial=profile)
    return render(request, 'profiles/edit_profile.html', {'form': form, 'profile_index': profile_index})