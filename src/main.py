from fastapi import FastAPI
from src.routes.chat_routes import router as chat_router
import uvicorn

app = FastAPI(title="SoundBot API", version="1.0.0")

app.include_router(chat_router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SoundBot API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)