from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

import app.db.entity.user as entity
import app.dto.user_request as create_user_request


async def find_user_by_id(db: AsyncSession, id: int) -> entity.User | None:
    """
    id로 유저를 조회하는 함수
    """
    result: Result = await db.execute(select(entity.User).where(entity.User.id == id))
    return result.scalars().first()


async def find_user_by_name(db: AsyncSession, name: str) -> entity.User | None:
    """
    name으로 유저를 조회하는 함수
    """
    result: Result = await db.execute(
        select(entity.User).where(entity.User.name == name)
    )
    return result.scalars().first()


async def create_user(
    db: AsyncSession, user: create_user_request.CreateUserRequest
) -> entity.User:
    """
    유저를 생성하는 함수
    """
    user = entity.User(**user.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(
    db: AsyncSession, user: create_user_request.UpdateUserRequest, original: entity.User
) -> entity.User:
    """
    유저를 업데이트하는 함수
    """
    original.name = user.name
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original

async def delete_user(db: AsyncSession, original: entity.User) -> None:
    """
    유저를 삭제하는 함수
    """
    await db.delete(original)
    await db.commit()