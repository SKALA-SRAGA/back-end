from typing import Union
from fastapi import APIRouter, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

from app.services.openai_service import get_streaming_message_from_openai
from app.services.log_script_service import logger
from app.services.rag_summarizer import summarize_meeting
from app.services.rag_pipeline import answer_question
from app.services.openai_vector_store import add_text
from fastapi.responses import StreamingResponse
from app.dto.message_request import MessageRequest
from app.dto.ask_request import AskRequest


router = APIRouter()

@router.post(
    "/translate",
    summary="Generate messages using OpenAI (streaming)",
)
async def get_generated_messages_with_header(
    data: MessageRequest,
    x_script_id: Union[str, None] = Header(default=None),
    db: AsyncSession = Depends(get_db)
):
    """
    ## Open AI에 번역 요청
    - Header: "x-script-id" 포함되어야 함!
    - data: MessageRequest
        - lang: 언어 코드 (e.g., "en-US", "ko-KR")
        - message: 번역할 메시지
    """

    await logger(db, data, x_script_id)
    await add_text(data.message, x_script_id)
    
    return StreamingResponse(
        get_streaming_message_from_openai(data), 
        media_type="text/event-stream"
    )

@router.post(
    "/ask",
    summary="Generate messages using OpenAI (streaming)",
)
async def ask_about_script(
    data: AskRequest
):
    """
    ## Open AI에 스크립트 질문 요청
    - data: AsyncRequest
        - script_id: 스크립트 ID
        - query: 질문할 메시지
    """

    return StreamingResponse(
        answer_question(
            query=data.query, 
            script_id=data.script_id
        ), 
        media_type="text/event-stream"
    )

@router.post(
    "/summary/{script_id}",
    summary="Summary messages using OpenAI (streaming)",
)
async def summarize_script(
    script_id: str
):
    """
    ## Open AI에 스크립트 요약 요청
    - script_id: 스크립트 ID
    - collection_num: 컬렉션 번호 (default=0)
    """

    return StreamingResponse(
        summarize_meeting(script_id=script_id), 
        media_type="text/event-stream"
    )