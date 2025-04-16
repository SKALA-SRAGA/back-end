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
  {"회의명": "예시: 2분기 마케팅 전략 회의"}
  {"회의일시": "2025-04-16 14:00"}
  {"회의요약": "..."}
  {"논의사항": ["...", "..."]}
  {"결정사항": ["...", "..."]}
  {"할 일": ["...", "..."]}
  {"미해결이슈": ["...", "..."]}
  {"주요키워드": ["...", "..."]}
  
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

    created_at = docs[0].metadata.get("created_at", "알 수 없음")
    print(created_at)
    # 2. 프롬프트 템플릿 생성
    prompt = PromptTemplate.from_template("""
    회의일시: {created_at}
                                          
    다음 회의록을 아래와 같이 항목별 JSON으로 나눠 요약해 주세요.
    각 항목은 개별 JSON 오브젝트로 줄바꿈해 출력하세요 (한 줄당 하나의 JSON):
                                          
    예시:                                                  
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
        buffer = ""
        summary_result = ""
        
        async for chunk in chain.astream(
            {"docs": docs_text, 
             "default": summary_contents,
             "created_at": created_at
             }):

            buffer += chunk
            summary_result += chunk

            while '}' in buffer:
                # 첫 번째 닫는 중괄호 위치를 찾고
                end_index = buffer.find('}') + 1
                # 그 위치까지 자름
                json_piece = buffer[:end_index]
                buffer = buffer[end_index:]
                # 전송
                yield f"data: {json_piece.strip()}\n\n"

        
        # 6. 요약 결과 저장
        await add_text(summary_result, script_id, 1)
        
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
        return