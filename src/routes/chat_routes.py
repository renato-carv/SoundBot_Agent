from fastapi import APIRouter, Request
from src.models.schemas import ChatRequest, ChatResponse
from src.controllers.chat_controller import ChatController
from src.utils.logger import logger

router = APIRouter(prefix="/v1", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, fastapi_request: Request):
    logger.info(f"New chat request from {fastapi_request.client.host} | user_id={request.user_id} | message='{request.message}'")
    response = ChatController.proccess_message(request.message, request.user_id)
    return response