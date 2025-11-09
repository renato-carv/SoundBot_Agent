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
