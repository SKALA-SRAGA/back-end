import os
from datetime import datetime
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
VECTOR_DB_PATH=os.getenv("VECTOR_DB_PATH")

# Chroma 벡터스토어 초기화
def init_vectordb(collection_num: int):

    collection_names = ['meeting_transcripts', 'meeting_summaries']        # 0: 회의 내용, 1: 회의 요약

    return Chroma(
        collection_name=collection_names[collection_num],                          # 컬렉션 이름 (카테고리처럼 생각)
        embedding_function=OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY),
        persist_directory=VECTOR_DB_PATH)     # 저장 경로

# 텍스트를 임베딩하고 DB에 저장하는 함수
async def add_text(text: str, script_id:str, collection_num:int=0):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 현재 시간

    source = "stt" if collection_num == 0 else "summary"

    doc = Document(page_content=text, metadata={
        "script_id": script_id,
        "source": source,
        "created_at":now
    })    # 문서 객체로 변환

    vectordb = init_vectordb(collection_num)
    vectordb.add_documents([doc])                      # 벡터 DB에 추가