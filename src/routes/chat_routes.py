from fastapi import APIRouter
from src.models.schemas import ChatRequest, ChatResponse
from src.controllers.chat_controller import ChatController

router = APIRouter(prefix="/v1", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return ChatController.proccess_message(request.message, request.user_id)