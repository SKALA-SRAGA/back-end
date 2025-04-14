import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
VECTOR_DB_PATH=os.getenv("VECTOR_DB_PATH")

# Chroma 벡터스토어 초기화
def init_vectordb():
    return Chroma(
        collection_name="my_texts",
        embedding_function=OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        ),
        persist_directory=VECTOR_DB_PATH
    )

# 텍스트를 임베딩하고 DB에 저장하는 함수
async def add_text(text: str, language_code: str, script_id:str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 현재 시간
    doc = Document(page_content=text, metadata={
        "script_id": script_id,
        "lang": language_code,
        "source": "stt",
        "created_at":now
    })    # 문서 객체로 변환
    vectordb = init_vectordb()
    vectordb.add_documents([doc])                      # 벡터 DB에 추가