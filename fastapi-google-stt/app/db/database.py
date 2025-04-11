from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs

ASYNC_DB_URL = "mysql+aiomysql://root:SqlDba-1@localhost:53303/sraga?charset=utf8mb4"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base(cls=AsyncAttrs)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
