# rag_summarizer.py
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.services.openai_vector_store import init_vectordb

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)


# 기본 요약 항목 템플릿 (사용자가 변경 가능하도록 외부로 분리)
default = """
- 회의 주제 요약
- 주요 결정 사항
- 남은 이슈/추후 할 일
- 참석자 요청/의견 요약
"""

prompt = PromptTemplate.from_template("""
다음 회의록 내용을 읽고, 아래 항목으로 요약해줘:

{default}

회의록:
{docs}
""")

# 회의 문서 요약 함수
def summarize_meeting(meeting_id: str, lang: str = "ko-KR", default:str = default):

    # 1. 벡터DB 초기화 및 문서 검색 (meeting_id + lang 필터)
    vectordb = init_vectordb()              

    docs = vectordb.similarity_search(
        query="회의 요약",                   # 의미 없는 쿼리로 문서만 불러올 수 있음
        k=100,
        filter={"meeting_id": "meeting1"}   # 회의 ID 기준
    )

    # 2. 문서가 없을 경우 예외 메시지 반환
    if not docs:
        return "해당 회의에 문서가 없습니다. 요약할 수 없습니다."
    
    # 3. 요약 체인 만들기(stuff 체인: 문서를 한 번에 처리)
    chain = load_summarize_chain(
        llm, chain_type="stuff", 
        prompt=prompt.partial(default=default),
        document_variable_name="docs")

    # 4. 요약 실행
    return chain.run(docs)
