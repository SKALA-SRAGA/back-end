import logging
from fastapi import APIRouter, HTTPException, Depends
import app.services.log_script_service as service
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

from app.dto.script_request import CreateScriptRequest

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/create")
async def create_script(request: CreateScriptRequest, db: AsyncSession = Depends(get_db)):
    """
    ## 스크립트 생성
    - request: 유저 ID
    """
    try:
        new_log_script = await service.create(db, request.user_id, request.name)
        return new_log_script
    except Exception as e:
        logger.error(f"Error creating log script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

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
    except HTTPException as http_exc:
        raise http_exc  # 상태코드 유지
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.get("/{script_id}")
async def get_script_by_id(script_id: str, db: AsyncSession = Depends(get_db)):
    """
    ## 스크립트 ID로 스크립트 조회
    - script_id: 스크립트 ID
    """
    try:
        scripts = await service.get_script_by_id(db, script_id)
        if scripts:
            return scripts
    except HTTPException as http_exc:
        raise http_exc  # 상태코드 유지
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")