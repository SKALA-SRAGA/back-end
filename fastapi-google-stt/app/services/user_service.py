from app.db.repository.user_repository import (
    find_user_by_id,
    find_user_by_name,
    create_user,
    update_user,
    delete_user,
)
from app.dto.user_request import CreateUserRequest, UpdateUserRequest
from app.db.entity.user import User
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_by_id(db: AsyncSession, id: str) -> dict:
    """
    id로 유저를 찾는 함수
    """
    return await find_user_by_id(db, id)

async def get_user_by_name(db: AsyncSession, name: str) -> User | None:
    """
    name으로 유저를 찾는 함수
    """
    return await find_user_by_name(db, name)

async def register(db: AsyncSession, user: CreateUserRequest) -> User:
    """
    유저를 등록하는 함수
    """
    return await create_user(db, user)

async def update(db: AsyncSession, user: UpdateUserRequest, original: User) -> User:
    """
    유저를 업데이트하는 함수
    """
    return await update_user(db, user, original)

async def delete(db: AsyncSession, original: User) -> None:
    """
    유저를 삭제하는 함수
    """
    return await delete_user(db, original)