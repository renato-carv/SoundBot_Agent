import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from src.utils.decorators import require_connection
from src.config.settings import settings


class SpotifyService:
    def __init__(self):
        try:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=settings.SPOTIFY_CLIENT_ID,
                    client_secret=settings.SPOTIFY_CLIENT_SECRET,
                )
            )
            print("Connected to Spotify")
        except Exception as e:
            print(f"Failed to connect to Spotify: {e}")
            self.sp = None

    @require_connection(attr_name="sp", service_name="Spotify")
    def search_track(self, query: str, limit: int = 10):
        try:
            results = self.sp.search(q=query, type="track", limit=limit)
            tracks = results.get("tracks", {}).get("items", [])
            if not tracks:
                return ["No tracks found"]
            return [f"{t['name']} - {t['artists'][0]['name']}" for t in tracks]
        except Exception as e:
            print(f"Failed to search track: {e}")
            return ["Failed to search track"]

    @require_connection(attr_name="sp", service_name="Spotify")
    def search_artist(self, name: str, limit: int = 3):
        try:
            results = self.sp.search(q=name, type="artist", limit=limit)
            artists = results.get("artists", {}).get("items", [])
            if not artists:
                return ["No artists found"]
            return [f"{a['name']} (popularidade: {a['popularity']})" for a in artists]
        except Exception as e:
            print(f"Failed to search artist: {e}")
            return ["Failed to search artist"]

    @require_connection(attr_name="sp", service_name="Spotify")
    def recommend_by_mood(self, mood: str, limit: int = 5):
        mood_map = {
            "feliz": "good vibes",  
            "triste": "sad",  
            "animado": "funk",  
            "calmo": "ambient",  
            "romântico": "jazz",  
            "energético": "rock",  
            "nostálgico": "90s hits",  
            "festa": "edm", 
            "focado": "lofi",  
            "pagode": "pagode",  
            "sertanejo": "sertanejo hits",  
            "bossa_nova": "bossa nova",  
            "samba": "samba",  
            "axé": "axé",  
            "mpb": "mpb",
            "eletrônico": "electronic",  
            "hip_hop": "hip-hop",  
            "reggae": "reggae",  
            "forró": "forró",  
            "trap": "trap",
        }

        genre_or_keyword = mood_map.get(mood.lower(), "pop")

        try:
            search_result = self.sp.search(q=genre_or_keyword, type="playlist", limit=3)
            playlists = search_result.get("playlists", {}).get("items", [])
            if not playlists:
                print(f"No playlists found for genre `{genre_or_keyword}`")
                return ["No playlists found"]
            tracks = []

            for pl in playlists:
                pl_items_result = self.sp.playlist_items(pl["id"], limit=limit)
                pl_items = pl_items_result.get("items", [])
                for item in pl_items:
                    t = item.get("track")
                    if t:
                        tracks.append(f"{t['name']} - {t['artists'][0]['name']}")
                if len(tracks) >= limit:
                    break

            if len(tracks) < limit:
                search_artists = self.sp.search(
                    q=genre_or_keyword, type="artist", limit=1
                )
                artists = search_artists.get("artists", {}).get("items", [])
                if artists:
                    artist_id = artists[0]["id"]
                    top_tracks_result = self.sp.artist_top_tracks(artist_id)
                    top_tracks = top_tracks_result.get("tracks", [])[
                        : limit - len(tracks)
                    ]
                    tracks.extend(
                        [f"{t['name']} - {t['artists'][0]['name']}" for t in top_tracks]
                    )

            if not tracks:
                return ["No tracks found"]
            return tracks[:limit]

        except Exception as e:
            print(f"Failed to recommend tracks for mood '{mood}': {e}")
            return ["Failed to recommend tracks"]

    @require_connection(attr_name="sp", service_name="Spotify")
    def get_track_preview(self, track_name: str):
        try:
            result = self.sp.search(q=track_name, type="track", limit=1)
            items = result["tracks"]["items"]
            if not items:
                return "Track not found"
            preview_url = items[0].get("preview_url")
            return preview_url or "No preview available"
        except Exception as e:
            print(f"Failed to get track preview for '{track_name}': {e}")
            return "Failed to get track preview"
