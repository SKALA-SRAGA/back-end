from typing import Union
from fastapi import APIRouter, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

from app.services.openai_service import get_streaming_message_from_openai
from app.services.log_script_service import logger
from app.services.rag_pipeline import answer_question
from app.services.openai_vector_store import add_text
from fastapi.responses import StreamingResponse
from app.dto.message_request import MessageRequest
from app.dto.ask_request import AskRequest

import logging

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
    logging.info("Header Test started")
    
    # return StreamingResponse(
    #     get_streaming_message_from_openai(data), media_type="text/event-stream"
    # )

    logging.info("Streaming started")

    await logger(db, data, x_script_id)
    await add_text(data.message, data.lang, x_script_id)
    
    return StreamingResponse(
        get_streaming_message_from_openai(data), 
        media_type="text/event-stream"
    )

@router.post(
    "/ask",
    summary="Generate messages using OpenAI (streaming)",
)
async def ask_about_script(
    data: AskRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    ## Open AI에 스크립트 질문 요청
    - Header: "x-script-id" 포함되어야 함!
    - data: MessageRequest
        - lang: 언어 코드 (e.g., "en-US", "ko-KR")
        - message: 질문할 메시지
    """

    # answer_question(query=data.message, script_id=data.script_id)

    return StreamingResponse(
        answer_question(
            query=data.query, 
            script_id=data.script_id
        ), 
        media_type="text/event-stream"
    )
    
    # return StreamingResponse(
    #     get_streaming_message_from_openai(data), media_type="text/event-stream"
    # )