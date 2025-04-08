from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse
from app.services.openai_service import get_streaming_message_from_openai
from app.models.message_request import MessageRequest

router = APIRouter()

@router.post(
    "/streaming/",
    summary="Generate messages using OpenAI (streaming)",
)
async def get_generated_messages_streaming(
    data: MessageRequest,
):
    """
    ## Send a prompt to OpenAI
    - message: str
    """
    print("Streaming started")
    return StreamingResponse(
        get_streaming_message_from_openai(data), media_type="text/event-stream"
    )