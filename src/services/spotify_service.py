import spotipy
import random
from spotipy.oauth2 import SpotifyClientCredentials
from src.utils.decorators import require_connection
from src.config.settings import settings
from src.utils.logger import logger 

class SpotifyService:
    def __init__(self):
        try:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=settings.SPOTIFY_CLIENT_ID,
                    client_secret=settings.SPOTIFY_CLIENT_SECRET,
                )
            )
            logger.info("Connected to Spotify")
        except Exception as e:
            logger.error(f"Failed to connect to Spotify: {e}")
            self.sp = None

    @require_connection(attr_name="sp", service_name="Spotify")
    def search_track(self, query: str, limit: int = 10):
        try:
            results = self.sp.search(q=query, type="track", limit=limit)
            tracks = results.get("tracks", {}).get("items", [])
            if not tracks:
                logger.warning(f"No tracks found for query '{query}'")
                return ["No tracks found"]
            return [f"{t['name']} - {t['artists'][0]['name']}" for t in tracks]
        except Exception as e:
            logger.error(f"Failed to search track '{query}': {e}")
            return ["Failed to search track"]

    @require_connection(attr_name="sp", service_name="Spotify")
    def search_artist(self, name: str, limit: int = 3):
        try:
            results = self.sp.search(q=name, type="artist", limit=limit)
            artists = results.get("artists", {}).get("items", [])
            if not artists:
                logger.warning(f"No artists found for '{name}'")
                return ["No artists found"]
            return [f"{a['name']} (popularidade: {a['popularity']})" for a in artists]
        except Exception as e:
            logger.error(f"Failed to search artist '{name}': {e}")
            return ["Failed to search artist"]

    @require_connection(attr_name="sp", service_name="Spotify")
    def recommend_by_mood_or_genre(self, mood: str = None, genre: str = None, limit: int = 5, exclude: set = None):
        exclude = exclude or set()

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
        }

        keyword = genre if genre else (mood_map.get(mood.lower()) if mood else "pop")
        tracks = []

        try:
            # Buscar playlists
            search_result = self.sp.search(q=keyword, type="playlist", limit=10)
            playlists = search_result.get("playlists", {}).get("items", []) if isinstance(search_result, dict) else []

            # Ordenar por número de seguidores
            playlists_with_followers = []
            for pl in playlists:
                try:
                    details = self.sp.playlist(pl["id"])
                    followers = details.get("followers", {}).get("total", 0)
                    playlists_with_followers.append((pl, followers))
                except:
                    continue
            playlists_with_followers.sort(key=lambda x: x[1], reverse=True)
            playlists = [pl for pl, _ in playlists_with_followers]

            # Extrair tracks
            for pl in playlists:
                try:
                    pl_items = self.sp.playlist_items(pl["id"], limit=limit*2).get("items", [])
                    for item in pl_items:
                        t = item.get("track")
                        if t and "name" in t and "artists" in t:
                            track_str = f"{t['name']} - {t['artists'][0]['name']}"
                            if track_str not in exclude:
                                tracks.append(track_str)
                    if len(tracks) >= limit:
                        break
                except:
                    continue

            # Shuffle e limita
            random.shuffle(tracks)
            tracks = tracks[:limit]

        except Exception as e:
            logger.error(f"Error recommending tracks for '{keyword}': {e}")

        if not tracks:
            logger.warning(f"No tracks found for keyword '{keyword}'")
            return ["No tracks found"]

        logger.info(f"Recommended tracks for '{keyword}' (filtered/shuffled): {tracks}")
        return tracks


    @require_connection(attr_name="sp", service_name="Spotify")
    def get_track_preview(self, track_name: str):
        try:
            result = self.sp.search(q=track_name, type="track", limit=1)
            items = result["tracks"]["items"]
            if not items:
                logger.warning(f"Track not found: '{track_name}'")
                return "Track not found"
            preview_url = items[0].get("preview_url")
            logger.info(f"Preview URL for '{track_name}': {preview_url}")
            return preview_url or "No preview available"
        except Exception as e:
            logger.error(f"Failed to get track preview for '{track_name}': {e}")
            return "Failed to get track preview"
