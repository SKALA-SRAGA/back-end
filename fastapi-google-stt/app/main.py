import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import stt_router, openai_router, user_router, script_router
from app.db.reset_database import reset_database

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

@app.on_event("startup")
async def on_startup():
    """애플리케이션 시작 시 데이터베이스 초기화"""
    await reset_database(force_reset=False)

app.include_router(stt_router.router, prefix="/stt", tags=["Google STT"])
app.include_router(openai_router.router, prefix="/openai", tags=["OpenAI"])
app.include_router(user_router.router, prefix="/user", tags=["User"])
app.include_router(script_router.router, prefix="/script", tags=["Script"])