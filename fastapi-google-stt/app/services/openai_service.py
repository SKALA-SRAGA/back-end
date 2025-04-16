import logging
import os
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_teddynote.messages import stream_response
from app.dto.message_request import MessageRequest

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=0.5, 
    openai_api_key=OPENAI_API_KEY, 
    streaming=True
)

templete='{text}을 {lang}로 번역해주세요. 번역 된 문장만 출력해주세요.'
prompt = PromptTemplate.from_template(templete)
output_parser = StrOutputParser()
chain = prompt | model | output_parser

async def get_streaming_message_from_openai(data: MessageRequest):
    try:
        # 스트리밍 응답 생성
        response = chain.astream({
            "text": data.message,
            "lang": data.lang
        })

        async for token in response:
            content = f"data: {token}\n\n"
            yield content
        yield "data: [DONE]\n\n"
    except Exception as e:
        # 에러 발생 시 스트리밍 방식으로 에러 메시지 반환
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")