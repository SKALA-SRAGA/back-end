# vector_retriever.py - 검색 유틸
from app.services.openai_vector_store import init_vectordb

def get_meeting_retriever(script_id: str, top_k: int = 5, collection_num:int =0):
    vectordb = init_vectordb(collection_num)
    
    return vectordb.as_retriever(
        search_kwargs={
            "k": top_k,
            "filter": {"script_id": script_id},
        }
    )