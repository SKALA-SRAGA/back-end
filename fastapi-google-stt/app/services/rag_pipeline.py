# rag_pipeline.py
from app.services.vector_retriever import get_meeting_retriever
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
import os
import json

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-4o-mini", 
    temperature=0.2, 
    openai_api_key=OPENAI_API_KEY,
    streaming=True
)

# 질의응답 함수
async def answer_question(query: str, script_id: str, collection_num: int=0):
    # 1. 회의 문서 리트리버 초기화
    retriever = get_meeting_retriever(script_id=script_id, collection_num=collection_num)
    
    # 2. 프롬프트 템플릿 생성
    prompt = ChatPromptTemplate.from_template("""
    당신은 회의 내용을 바탕으로 질문에 답변하는 도우미입니다.
    
    회의 내용:
    {context}
    
    질문: {question}
    
    답변:
    """)
    
    # 3. LCEL 방식으로 RAG 체인 구성
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    try:
        # 4. 응답 스트리밍
        # 먼저 모델 응답 스트리밍
        async for chunk in rag_chain.astream(query):
            yield f"data: {chunk}\n\n"
        
        # # 5. 스트리밍 완료 후 소스 문서 전송
        # docs = await retriever.ainvoke(query)
        # for doc in docs:
        #     # source_info = {
        #     #     "content": doc.page_content,
        #     #     "metadata": doc.metadata
        #     # }
        #     yield f"data: Content: {doc.page_content}\n\n"
            
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"