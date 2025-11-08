import pytest
from src.services.spotify_service import SpotifyService

@pytest.fixture
def spotify():
    return SpotifyService()

@pytest.mark.parametrize("mood", [
    "feliz", "triste", "animado", "calmo", "romântico",
    "energético", "nostálgico", "festa", "focado",
    "pagode", "sertanejo", "bossa_nova", "samba", "axé",
    "mpb", "eletrônico", "hip_hop", "reggae", "forró", "trap"
])
def test_recommend_by_mood_returns_tracks(spotify, mood):
    tracks = spotify.recommend_by_mood(mood, limit=5)
    print(f"Mood: {mood} -> Tracks: {tracks}")
    assert tracks is not None, f"Falha ao recomendar para o mood {mood}"
    assert isinstance(tracks, list), "O retorno deve ser uma lista"
    assert len(tracks) > 0, f"Nenhuma track encontrada para {mood}"

def test_search_track_returns_tracks(spotify):
    tracks = spotify.search_track("Shape of You", limit=3)
    assert isinstance(tracks, list)
    assert any("Shape of You" in t for t in tracks)

def test_search_artist_returns_artists(spotify):
    artists = spotify.search_artist("Adele", limit=3)
    assert isinstance(artists, list)
    assert any("Adele" in a for a in artists)
