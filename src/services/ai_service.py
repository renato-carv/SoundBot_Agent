import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from src.config.settings import settings
from src.utils.logger import logger  # ✅ Importando o logger configurado

class AIService:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            groq_api_key=settings.GROQ_API_KEY
        )
        logger.info("AIService initialized with model llama-3.1-8b-instant")

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
        logger.info(f"Interpreting user request: '{text}'")

        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()

            logger.debug(f"Raw LLM response: {content}")

            # Remove possíveis delimitadores de bloco de código Markdown
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(content)
            logger.info(f"Successfully interpreted request: {parsed}")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e} | Response content: {content}")
        except Exception as e:
            logger.exception(f"Error interpreting request: {e}")

        # Fallback padrão em caso de erro
        return {
            "acao": "desconhecido",
            "humor": None,
            "artista": None,
            "musica": None,
        }

    def generate_reply(
        self,
        context: str,
        recommendations: list,
        mood: str = None,
        artist: str = None,
        song: str = None
    ) -> str:
        system_prompt = """
        Você é um assistente musical amigável e natural.
        Retorne **apenas** um JSON válido no formato:
        {
        "reply": "Mensagem simpáticas e humanas, sem citar os nomes das músicas. De hipótese nenhuma, seja grosseiro.",
        "mood": "<humor_detectado ou null>",
        "recommendations": ["música - artista", ...]
        }

        Regras importantes:
        - O campo "reply" deve conter uma frase natural (ex: "Acho que essas músicas combinam com seu humor! 🎧")
        - NUNCA inclua os nomes das músicas no "reply"
        - O campo "recommendations" deve conter exatamente as músicas listadas
        - O texto deve estar em português e soar humano
        - NÃO coloque markdown nem blocos de código
        """

        user_context = f"""
        Contexto: {context}
        Humor detectado: {mood}
        Artista: {artist}
        Música: {song}
        Recomendações: {recommendations if recommendations else 'nenhuma encontrada'}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_context)
        ]

        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()

            # remove ```json e outros delimitadores
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            data = json.loads(content)

            # garante que reply sempre exista
            reply = data.get("reply", "Espero que goste dessas músicas! 🎶")
            mood = data.get("mood", mood)
            recommendations = data.get("recommendations", recommendations)

            logger.info(f"AI formatted reply: {data}")
            return reply  # só retornamos o texto pro ChatController

        except json.JSONDecodeError:
            logger.warning(f"LLM did not return JSON. Raw: {response.content}")
            return "Aqui estão algumas músicas que acho que você vai gostar! 🎧"
        except Exception as e:
            logger.error(f"Error generating reply: {e}", exc_info=True)
            return "Tive um probleminha para formular a resposta agora, mas posso tentar de novo se quiser!"
