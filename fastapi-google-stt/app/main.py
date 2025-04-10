import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import stt, openai

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

app.include_router(stt.router, prefix="/stt", tags=["Google STT"])
app.include_router(openai.router, prefix="/openai", tags=["OpenAI"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Google Speech-to-Text service!"}