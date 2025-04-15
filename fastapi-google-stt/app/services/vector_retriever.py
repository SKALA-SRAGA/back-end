# vector_retriever.py - 검색 유틸
from app.services.openai_vector_store import init_vectordb

def get_meeting_retriever(script_id: str, lang: str = "ko-KR", top_k: int = 5):
    vectordb = init_vectordb()
    
    return vectordb.as_retriever(
        search_kwargs={
            "k": top_k,
            "filter": {
                "$and": [
                    {"script_id": script_id},
                    {"lang": lang},
                ]
            }
        }
    )