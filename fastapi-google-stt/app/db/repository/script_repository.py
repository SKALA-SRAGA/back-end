from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

import app.db.entity.script as entity

async def find_script_by_id(db: AsyncSession, id: int) -> entity.Script | None:
    """
    id로 스크립트를 조회하는 함수
    """
    result: Result = await db.execute(select(entity.Script).where(entity.Script.id == id))
    return result.scalars().first()

async def find_script_by_user_id(db: AsyncSession, user_id: int) -> entity.Script | None:
    """
    user_id로 스크립트를 조회하는 함수
    """
    result: Result = await db.execute(
        select(entity.Script).where(entity.Script.user_id == user_id)
    )
    return result.scalars().all()

async def create_script(
    db: AsyncSession, script: entity.Script
) -> entity.Script:
    """
    스크립트를 생성하는 함수
    """
    db.add(script)
    await db.commit()
    await db.refresh(script)
    return script

async def update_script(
    db: AsyncSession, script: entity.Script, original: entity.Script
) -> entity.Script:
    """
    스크립트를 업데이트하는 함수
    """
    original.script = script.script
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original

async def delete_script(db: AsyncSession, original: entity.Script) -> None:
    """
    스크립트를 삭제하는 함수
    """
    await db.delete(original)
    await db.commit()