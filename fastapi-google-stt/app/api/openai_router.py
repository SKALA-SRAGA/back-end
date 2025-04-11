from typing import Union
from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from app.services.openai_service import get_streaming_message_from_openai
from app.dto.message_request import MessageRequest
from app.services.log_script_service import logger

router = APIRouter()

@router.post(
    "/streaming",
    summary="Generate messages using OpenAI (streaming)",
)
async def get_generated_messages_streaming(
    data: MessageRequest,
):
    """
    ## Open AI에 번역 요청
    - data: MessageRequest
        - lang: 언어 코드 (e.g., "en-US", "ko-KR")
        - message: 번역할 메시지
    """
    print("Streaming started")
    return StreamingResponse(
        get_streaming_message_from_openai(data), media_type="text/event-stream"
    )

@router.post(
    "/header-test",
    summary="Generate messages using OpenAI (streaming) - header test",
)
async def get_generated_messages_streaming(
    data: MessageRequest,
    x_user_id: Union[str, None] = Header(default=None),
):
    """
    ## Open AI에 번역 요청
    - Header: "x-user-id" 포함되어야 함!
    - data: MessageRequest
        - lang: 언어 코드 (e.g., "en-US", "ko-KR")
        - message: 번역할 메시지
    """
    print("Header Test started")
    
    # return StreamingResponse(
    #     get_streaming_message_from_openai(data), media_type="text/event-stream"
    # )

    return logger(data, x_user_id)