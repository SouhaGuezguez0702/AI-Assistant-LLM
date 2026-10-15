from fastapi import APIRouter

from backend.app.services.chat_service import ChatService
from backend.app.models.chat_models import ChatRequest, ChatResponse

router = APIRouter()

chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    user_message = request.messages[-1].content

    history = [
        {"role": m.role, "content": m.content}
        for m in request.messages[:-1]
        if m.role in ("user", "assistant")
    ]

    answer = chat_service.ask(user_message, history=history)

    return ChatResponse(response=answer)