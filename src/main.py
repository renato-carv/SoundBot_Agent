from fastapi import FastAPI
from src.routes.chat_routes import router as chat_router
from src.utils.logger import logger
import uvicorn

app = FastAPI(title="SoundBot API", version="1.0.0")

# Inclui as rotas
app.include_router(chat_router)

@app.on_event("startup")
async def startup_event():
    logger.info("SoundBot API started successfully")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SoundBot API"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
