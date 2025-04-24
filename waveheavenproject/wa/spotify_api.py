import requests
from django.conf import settings
from urllib.parse import urlencode


def get_auth_url():
    query_params = urlencode({
        "client_id": settings.SPOTIPY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIPY_REDIRECT_URI,
        "scope": "user-read-playback-state user-modify-playback-state streaming user-read-currently-playing",
    })
    return f"https://accounts.spotify.com/authorize?{query_params}"


def get_token_from_code(code):
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIPY_REDIRECT_URI,
        "client_id": settings.SPOTIPY_CLIENT_ID,
        "client_secret": settings.SPOTIPY_CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error al obtener el token: {response.text}")
    
    return response.json()


def get_current_playback(token):
    url = "https://api.spotify.com/v1/me/player"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error al obtener reproducción actual: {response.text}")
    
    return response.json()


# OPCIONAL — Obtener usuario actual
def get_user_profile(token):
    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error al obtener usuario: {response.text}")
    
    return response.json()


# OPCIONAL — Crear playlist
def create_playlist(token, user_id, name="WaveHeaven Playlist", description="Generada automáticamente"):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "name": name,
        "description": description,
        "public": True
    }

    response = requests.post(url, json=body, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"Error al crear playlist: {response.text}")
    
    return response.json()


# OPCIONAL — Añadir canciones a playlist
def add_tracks_to_playlist(token, playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "uris": track_uris
    }

    response = requests.post(url, json=body, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"Error al añadir canciones: {response.text}")