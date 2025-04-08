from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import stt, openai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stt.router, prefix="/stt", tags=["Google STT"])
app.include_router(openai.router, prefix="/openai", tags=["OpenAI"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Google Speech-to-Text service!"}