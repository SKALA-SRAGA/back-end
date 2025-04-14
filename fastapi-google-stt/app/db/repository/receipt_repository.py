from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

import app.db.entity.receipt as entity

async def find_receipt_by_id(db: AsyncSession, id: int) -> entity.Receipt | None:
    """
    id로 영수증을 조회하는 함수
    """
    result: Result = await db.execute(select(entity.Receipt).where(entity.Receipt.id == id))
    return result.scalars().first()

async def find_receipt_by_user_id(db: AsyncSession, user_id: int) -> entity.Receipt | None:
    """
    user_id로 영수증을 조회하는 함수
    """
    result: Result = await db.execute(
        select(entity.Receipt).where(entity.Receipt.user_id == user_id)
    )
    return result.scalars().all()

async def create(
    db: AsyncSession, receipt: entity.Receipt
) -> entity.Receipt:
    """
    영수증을 생성하는 함수
    """
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)
    return receipt

async def delete(
    db: AsyncSession, original: entity.Receipt
) -> entity.Receipt:
    """
    영수증을 삭제하는 함수
    """
    await db.delete(original)
    await db.commit()
    return original