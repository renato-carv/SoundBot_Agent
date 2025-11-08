from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from src.config.settings import settings
import json


class AIService:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant", temperature=0.7, groq_api_key=settings.GROQ_API_KEY
        )

    def interpret_request(self, text: str) -> dict:
        system_prompt = """
            Você é um assistente musical que interpreta pedidos dos usuários e converte em JSON estruturado.

            Retorne SOMENTE o JSON, no formato:
            {
            "acao": "recomendar" | "buscar_artista" | "buscar_musica" | "desconhecido",
            "humor": "feliz" | "triste" | "animado" | "calmo" | "romântico" | "energético" | "nostálgico" | "festa" | "focado" | null,
            "artista": string | null,
            "musica": string | null
            }
        """

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=text)]

        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()

            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            return json.loads(content)

        except Exception as e:
            print(f"Failed to interpret request: {e}")
            return {
                "acao": "desconhecido",
                "humor": None,
                "artista": None,
                "musica": None,
            }
