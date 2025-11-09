import redis
import json
from src.config.settings import settings

class MemoryManager:
    def __init__(self):
        try:
            self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"⚠️ Failed to connect to Redis: {e}")
            self.redis_client = None

        self.mem_limit = settings.MEM_LIMIT

    def _get_key(self, user_id: str):
        return f"chat:{user_id}"

    def get_context(self, user_id: str):
        if not self.redis_client:
            return []

        data = self.redis_client.get(self._get_key(user_id))
        return json.loads(data) if data else []

    def append_context(self, user_id: str, message: str, reply: str, recommendations: list = None):
        if not self.redis_client:
            return

        key = self._get_key(user_id)
        context = self.get_context(user_id)
        context.append({
            "user": message,
            "bot": reply,
            "recommendations": recommendations or []
        })

        if len(context) > self.mem_limit:
            context = context[-self.mem_limit:]

        self.redis_client.set(key, json.dumps(context))


    def clear_context(self, user_id: str):
        if self.redis_client:
            self.redis_client.delete(self._get_key(user_id))

    def get_previous_recommendations(self, user_id: str) -> set:
        context = self.get_context(user_id)
        recs = set()
        for entry in context:
            recs.update(entry.get("recommendations", []))
        return recs

