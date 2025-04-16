import logging
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
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def get_user_by_id(db: AsyncSession, id: str) -> dict:
    """
    id로 유저를 찾는 함수
    """
    try:
        user = await find_user_by_id(db, id)
        if not user:
            # 유저가 없을 경우 404 상태 코드 반환
            raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
        return user
    except HTTPException:
        # 이미 처리된 HTTPException은 그대로 전달
        raise
    except Exception as e:
        logger.error(f"Error in get_user_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user by ID")

async def get_user_by_name(db: AsyncSession, name: str) -> User | None:
    """
    name으로 유저를 찾는 함수
    """
    try:
        user = await find_user_by_name(db, name)
        if not user:
            # 유저가 없을 경우 404 상태 코드 반환
            raise HTTPException(status_code=404, detail=f"User with name {name} not found")
        return user
    except HTTPException:
        # 이미 처리된 HTTPException은 그대로 전달
        raise
    except Exception as e:
        logger.error(f"Error in get_user_by_name: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user by name")

async def register(db: AsyncSession, user: CreateUserRequest) -> User:
    """
    유저를 등록하는 함수
    """
    try:
        new_user = await create_user(db, user)
        if not new_user:
            raise HTTPException(status_code=500, detail="Failed to register user")
        return new_user
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

async def update(db: AsyncSession, user: UpdateUserRequest, original: User) -> User:
    """
    유저를 업데이트하는 함수
    """
    try:
        updated_user = await update_user(db, user, original)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update user")
        return updated_user
    except Exception as e:
        logger.error(f"Error in update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

async def delete(db: AsyncSession, original: User) -> None:
    """
    유저를 삭제하는 함수
    """
    try:
        result = await delete_user(db, original)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to delete user")
        return result
    except Exception as e:
        logger.error(f"Error in delete: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")