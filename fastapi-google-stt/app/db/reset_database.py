from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

from app.db.database import Base

import app.db.entity


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

ASYNC_DB_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True, pool_recycle=3600)

async def reset_database(force_reset: bool = False):
    async with async_engine.begin() as conn:
        if force_reset:
            # 기존 테이블 삭제 후 재생성
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        else:
            # 테이블이 없는 경우에만 생성
            await conn.run_sync(Base.metadata.create_all)
        
    await async_engine.dispose()
