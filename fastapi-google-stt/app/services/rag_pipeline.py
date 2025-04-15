# rag_pipeline.py
from app.services.vector_retriever import get_meeting_retriever
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA  # LangChain의 질의응답 체인 (LLM + Retriever)
import os

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2, openai_api_key=os.getenv("OPENAI_API_KEY"))

# 질의응답 함수
def answer_question(query: str, script_id: str, collection_num: int=0):

    # 1. 회의 문서 리트리버 초기화 (meeting_id & lang 필터 적용)
    retriever = get_meeting_retriever(script_id=script_id, collection_num=collection_num)

    # 2. Retrieval QA 체인 생성 (LLM + Retriever 연결)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    # 3. 질의 실행 → 답변 + 문서 반환
    response = qa_chain(query)
    return response["result"], response["source_documents"]