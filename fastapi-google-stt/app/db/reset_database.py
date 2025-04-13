from sqlalchemy.ext.asyncio import create_async_engine

from app.db.database import Base

import app.db.entity

ASYNC_DB_URL = "mysql+aiomysql://root:SqlDba-1@localhost:53303/sraga?charset=utf8mb4"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

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
