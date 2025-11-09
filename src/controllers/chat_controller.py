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
        genre = intent.get("genero")
        artist = intent.get("artista")
        song = intent.get("musica")

        recommendations = []
        reply = ""

        try:
            # Recupera histórico de recomendações
            previous_recs = memory_manager.get_previous_recommendations(user_id)

            if action == "buscar_musica" and song:
                recommendations = spotify_service.search_track(song)
                context = f"O usuário pediu para buscar a música '{song}'."

            elif action == "buscar_artista" and artist:
                recommendations = spotify_service.search_track(f"artist:{artist}")
                context = f"O usuário pediu para ver músicas do artista '{artist}'."

            elif action == "recomendar":
                recommendations = spotify_service.recommend_by_mood_or_genre(
                    mood=mood,
                    genre=genre,
                    limit=5,
                    exclude=previous_recs
                )
                if genre:
                    context = f"O usuário quer recomendações de músicas do gênero '{genre}'."
                elif mood:
                    context = f"O usuário quer recomendações de músicas para um humor {mood}."
                else:
                    context = "O usuário quer recomendações de músicas."

            else:
                context = "O pedido do usuário não foi claramente compreendido."

            reply = ai_service.generate_reply(context, recommendations, mood, artist, song)

        except Exception as e:
            logger.error(f"Error in ChatController for user {user_id}: {e}", exc_info=True)
            reply = "Desculpe, houve um problema ao buscar suas recomendações."
            recommendations = []

        # Armazena mensagem, reply e recommendations no Redis
        memory_manager.append_context(user_id, message, reply, recommendations)
        logger.info(f"Context updated for user {user_id}")

        return ChatResponse(reply=reply, mood=mood, genre=genre, recommendations=recommendations)
