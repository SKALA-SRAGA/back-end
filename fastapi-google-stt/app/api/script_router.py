import logging
from fastapi import APIRouter, Depends
import app.services.log_script_service as service
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/create/{user_id}")
async def create_script(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    ## 스크립트 생성
    - user_id: 유저 ID
    """
    try:
        new_log_script = await service.create(db, user_id)
        return new_log_script
    except Exception as e:
        logger.error(f"Error creating log script: {str(e)}")
        return {"message": "Internal server error"}, 500

@router.get("/all/{user_id}")
async def get_scripts_by_user_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    ## 유저 ID로 스크립트 조회
    - user_id: 유저 ID
    """
    try:
        scripts = await service.get_scripts_by_user_id(db, user_id)
        if scripts:
            return scripts
        else:
            return {"message": "No scripts found for this user"}, 404
    except Exception as e:
        logger.error(f"Error retrieving scripts: {str(e)}")
        return {"message": "Internal server error"}, 500
    
@router.get("/{script_id}")
async def get_script_by_id(script_id: str, db: AsyncSession = Depends(get_db)):
    """
    ## 스크립트 ID로 스크립트 조회
    - script_id: 스크립트 ID
    """
    try:
        script = await service.get_script_by_id(db, script_id)
        if script:
            return script
        else:
            return {"message": "Script not found"}, 404
    except Exception as e:
        logger.error(f"Error retrieving script: {str(e)}")
        return {"message": "Internal server error"}, 500