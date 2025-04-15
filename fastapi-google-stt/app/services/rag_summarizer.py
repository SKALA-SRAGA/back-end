# rag_summarizer.py
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.openai_vector_store import (
    init_vectordb,
    add_text
)
import os

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-4o-mini", 
    temperature=0,
    streaming=True,
    openai_api_key=OPENAI_API_KEY
)

# 기본 요약 항목 템플릿 (사용자가 변경 가능하도록 외부로 분리)
summary_default = """
- 회의 주제 요약
- 주요 결정 사항
- 남은 이슈/추후 할 일
- 참석자 요청/의견 요약
"""

# 함수 시그니처는 원래대로 유지하고 내부 로직만 변경
async def summarize_meeting(script_id: str, collection_num: int=0, summary_contents: str = summary_default):

    # 1. 벡터DB 초기화 및 문서 검색
    vectordb = init_vectordb(collection_num)
    docs = vectordb.similarity_search(
        query="회의 요약",
        k=100,
        filter={"script_id": script_id}
    )
    
    if not docs:
        yield "data: 해당 회의에 문서가 없습니다. 요약할 수 없습니다.\n\n"
        return

    # 2. 프롬프트 템플릿 생성
    prompt = PromptTemplate.from_template("""
    다음은 회의록입니다. 핵심 내용을 요약해 주세요.:

    {default}

    회의록:
    {docs}
    """)

    try:
        # 3. 문서 텍스트 결합
        docs_text = "\n\n".join([doc.page_content for doc in docs])
        
        # 4. 요약 체인 생성 (LCEL 방식)
        chain = (
            prompt 
            | llm 
            | StrOutputParser()
        )
        
        # 5. 요약 스트리밍 실행
        summary_result = ""
        async for chunk in chain.astream({"docs": docs_text, "default": summary_contents}):
            summary_result += chunk
            yield f"data: {chunk}\n\n"
        
        # 6. 요약 결과 저장
        await add_text(summary_result, script_id, 1)
        
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
        return