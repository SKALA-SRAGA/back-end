import logging
from fastapi import APIRouter, Depends
import app.services.user_service as service
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

router = APIRouter()

# 로깅 설정
logger = logging.getLogger(__name__)

@router.get("/{name}")
async def get_user(name: str, db: AsyncSession = Depends(get_db)):
    """
    ## 유저 정보 조회
    - name: 유저 이름
    """
    try:
        user = await service.get_user_by_name(db, name)
        if user:
            return user
        else:
            return {"message": "User not found"}, 404
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        return {"message": "Internal server error"}, 500

@router.get("/id/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    ## 유저 정보 조회
    - user_id: 유저 ID
    """
    try:
        user = await service.get_user_by_id(db, user_id)
        if user:
            return user
        else:
            return {"message": "User not found"}, 404
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        return {"message": "Internal server error"}, 500

@router.post("/register")
async def register_user(user: service.CreateUserRequest, db: AsyncSession = Depends(get_db)):
    """
    ## 유저 등록
    - user: CreateUserRequest
        - name: 유저 이름
    """
    try:
        new_user = await service.register(db, user)
        return new_user
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return {"message": "Internal server error"}, 500