# vector_store_openai.py - vector 저장
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

load_dotenv()

# Chroma 벡터스토어 초기화
def init_vectordb():
    return Chroma(
        collection_name="my_texts",                        # 컬렉션 이름 (카테고리처럼 생각)
        embedding_function=OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")),
        persist_directory="app/vector_store/chroma_db")     # 저장 경로

# 텍스트를 임베딩하고 DB에 저장하는 함수
def add_text(text: str, language_code: str, meeting_id:str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 현재 시간
    doc = Document(page_content=text, metadata={
        "meeting_id": meeting_id,
        "lang": language_code,
        "source": "stt",
        "created_at":now
    })    # 문서 객체로 변환
    vectordb = init_vectordb()
    vectordb.add_documents([doc])                      # 벡터 DB에 추가
    vectordb.persist()                                 # 디스크 저장