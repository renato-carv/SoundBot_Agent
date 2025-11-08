from fastapi import APIRouter
from src.models.schemas import ChatRequest, ChatResponse
from src.services.ai_service import AIService
from src.services.spotify_service import SpotifyService
from src.utils.memory_manager import MemoryManager

ai_service = AIService()
spotify_service = SpotifyService()
memory_manager = MemoryManager()

class ChatController:
    @staticmethod
    def proccess_message(message: str, user_id: str) -> ChatResponse:
        intent = ai_service.interpret_request(message)

        action = intent.get("acao")
        mood = intent.get("humor")
        artist = intent.get("artista")
        song = intent.get("musica")

        reply = ""
        recommendations = []

        if action == "buscar_musica" and song:
            recommendations = spotify_service.search_track(song)
            reply = f"Encontrei algumas músicas que correspondem a '{song}':"

        elif action == "buscar_artista" and artist:
            recommendations = spotify_service.search_track(f"artist:{artist}")
            reply = f"Encontrei algumas músicas do artista '{artist}':"

        elif action == "recomendar" and mood:
            recommendations = spotify_service.recommend_by_mood(mood)
            reply = f"Essas músicas combinam com um humor {mood}:"
            
        else:
            reply = "Desculpe, não entendi muito bem seu pedido."

        memory_manager.append_context(user_id, message, reply)

        return ChatResponse(reply=reply, mood=mood, recommendations=recommendations)
