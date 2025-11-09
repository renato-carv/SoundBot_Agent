from src.models.schemas import ChatResponse
from src.services.ai_service import AIService
from src.services.spotify_service import SpotifyService
from src.utils.memory_manager import MemoryManager
from src.utils.logger import logger

ai_service = AIService()
spotify_service = SpotifyService()
memory_manager = MemoryManager()

class ChatController:
    @staticmethod
    def proccess_message(message: str, user_id: str) -> ChatResponse:
        logger.info(f"Processing message from user {user_id}: '{message}'")

        intent = ai_service.interpret_request(message)
        logger.info(f"Interpreted intent: {intent}")

        action = intent.get("acao")
        mood = intent.get("humor")
        artist = intent.get("artista")
        song = intent.get("musica")

        reply = ""
        recommendations = []

        try:
            if action == "buscar_musica" and song:
                logger.info(f"Searching for track: '{song}'")
                recommendations = spotify_service.search_track(song) or []
                reply = f"Encontrei algumas músicas que correspondem a '{song}':"

            elif action == "buscar_artista" and artist:
                logger.info(f"Searching for artist: '{artist}'")
                recommendations = spotify_service.search_track(f"artist:{artist}") or []
                reply = f"Encontrei algumas músicas do artista '{artist}':"

            elif action == "recomendar" and mood:
                logger.info(f"Recommending songs for mood: '{mood}'")
                recommendations = spotify_service.recommend_by_mood(mood) or []
                reply = f"Essas músicas combinam com um humor {mood}:"
                
            else:
                logger.warning(f"Unrecognized request intent for message: '{message}'")
                reply = "Desculpe, não entendi muito bem seu pedido."
                recommendations = []

        except Exception as e:
            logger.error(f"Error in ChatController for user {user_id}: {e}", exc_info=True)
            reply = "Desculpe, houve um problema ao buscar suas recomendações."
            recommendations = []

        memory_manager.append_context(user_id, message, reply)
        logger.info(f"Context updated for user {user_id}")

        return ChatResponse(reply=reply, mood=mood, recommendations=recommendations)
