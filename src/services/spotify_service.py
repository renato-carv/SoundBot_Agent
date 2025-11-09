import spotipy
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
        tracks = []

        try:
            search_result = self.sp.search(q=genre_or_keyword, type="playlist", limit=10)

            if search_result is None:
                logger.error(f"Spotify search returned None for '{genre_or_keyword}'")
                playlists = []
            elif not isinstance(search_result, dict):
                logger.error(f"Spotify search returned invalid type: {type(search_result)}")
                playlists = []
            else:
                playlists_obj = search_result.get("playlists")
                if not playlists_obj or not isinstance(playlists_obj, dict):
                    logger.warning(f"No playlists object found for '{genre_or_keyword}'")
                    playlists = []
                else:
                    playlists = playlists_obj.get("items", [])

            if not playlists:
                logger.warning(f"No playlists found for '{genre_or_keyword}'")

            playlists_with_followers = []
            for pl in playlists:
                try:
                    # VERIFICAÇÃO ADICIONAL PARA playlist
                    if not pl or not isinstance(pl, dict) or "id" not in pl:
                        continue
                        
                    details = self.sp.playlist(pl["id"])
                    
                    # VERIFICAÇÃO PARA details
                    if details is None or not isinstance(details, dict):
                        continue
                        
                    followers = details.get("followers", {}).get("total", 0)
                    playlists_with_followers.append((pl, followers))
                except Exception as e:
                    logger.warning(f"Failed to get playlist details for '{pl.get('name', pl.get('id'))}': {e}")
                    continue

            playlists_with_followers.sort(key=lambda x: x[1], reverse=True)
            playlists = [pl for pl, _ in playlists_with_followers]

            for pl in playlists:
                try:
                    # VERIFICAÇÃO ADICIONAL
                    if not pl or not isinstance(pl, dict) or "id" not in pl:
                        continue
                        
                    pl_items_result = self.sp.playlist_items(pl["id"], limit=limit)
                    
                    # VERIFICAÇÃO PARA pl_items_result
                    if pl_items_result is None or not isinstance(pl_items_result, dict):
                        continue
                        
                    pl_items = pl_items_result.get("items", [])
                    for item in pl_items:
                        if not item or not isinstance(item, dict):
                            continue
                            
                        t = item.get("track")
                        if t and isinstance(t, dict):
                            track_name = t.get('name')
                            artist_name = t['artists'][0]['name'] if t.get('artists') else 'Unknown Artist'
                            if track_name:
                                tracks.append(f"{track_name} - {artist_name}")
                    if len(tracks) >= limit:
                        break
                except Exception as e:
                    logger.error(f"Error getting playlist items for '{pl.get('name')}': {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching playlists for '{genre_or_keyword}': {e}")

        if len(tracks) < limit:
            try:
                search_artists = self.sp.search(q=genre_or_keyword, type="artist", limit=5)
                
                if search_artists is None or not isinstance(search_artists, dict):
                    artists = []
                else:
                    artists_data = search_artists.get("artists", {})
                    artists = artists_data.get("items", []) if isinstance(artists_data, dict) else []
                    
                for artist in artists:
                    try:
                        if not artist or not isinstance(artist, dict) or "id" not in artist:
                            continue
                            
                        top_tracks_result = self.sp.artist_top_tracks(artist["id"])
                        
                        if top_tracks_result is None or not isinstance(top_tracks_result, dict):
                            continue
                            
                        top_tracks = top_tracks_result.get("tracks", [])[:limit - len(tracks)]
                        for t in top_tracks:
                            if t and isinstance(t, dict):
                                track_name = t.get('name')
                                artist_name = t['artists'][0]['name'] if t.get('artists') else 'Unknown Artist'
                                if track_name:
                                    tracks.append(f"{track_name} - {artist_name}")
                        if len(tracks) >= limit:
                            break
                    except Exception as e:
                        logger.error(f"Error getting top tracks for artist '{artist.get('name')}': {e}")
                        continue
            except Exception as e:
                logger.error(f"Error searching artists for '{genre_or_keyword}': {e}")

        if len(tracks) < limit:
            try:
                search_tracks = self.sp.search(q=genre_or_keyword, type="track", limit=limit - len(tracks))
                
                if search_tracks is None or not isinstance(search_tracks, dict):
                    track_items = []
                else:
                    tracks_data = search_tracks.get("tracks", {})
                    track_items = tracks_data.get("items", []) if isinstance(tracks_data, dict) else []
                    
                for t in track_items:
                    if t and isinstance(t, dict):
                        track_name = t.get('name')
                        artist_name = t['artists'][0]['name'] if t.get('artists') else 'Unknown Artist'
                        if track_name:
                            tracks.append(f"{track_name} - {artist_name}")
            except Exception as e:
                logger.error(f"Error searching tracks for '{genre_or_keyword}': {e}")

        if not tracks:
            logger.warning(f"No tracks found for mood '{mood}'")
            return ["No tracks found"]

        logger.info(f"Recommended tracks for mood '{mood}': {tracks[:limit]}")
        return tracks[:limit]

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
