from fastapi import APIRouter, UploadFile, File, Form, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from fastapi.responses import FileResponse
from fastapi import HTTPException
from typing import List
import shutil
import os
from pathlib import Path
import json

from app.services.docs_service import create_expense_report
from app.services.receipt_service import (
    process_multiple_images,
    create_receipt,
    get_my_receipts,
    generate_base64_uuid
)

router = APIRouter()

# 임시 저장소 경로
TEMP_DIR = Path("temp_images")
OUTPUT_DIR = Path("output")
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def process_receipts(
    files: List[UploadFile] = File(...), 
    user_id: int = Form(...),
    name: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """영수증 이미지를 처리하고 문서를 생성합니다."""

    # 임시 파일 저장
    image_paths = []
    try:
        # 파일 저장
        for file in files:
            temp_path = TEMP_DIR / file.filename
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_paths.append(str(temp_path))

        # 이미지 처리 및 JSON 생성
        results = process_multiple_images(image_paths)
        json_path = TEMP_DIR / "receipt_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        # 문서 생성
        receipt_id = generate_base64_uuid()
        output_path = OUTPUT_DIR / f"{receipt_id}_expense_report.docx"
        create_expense_report(str(json_path), str(output_path))

        await create_receipt(
            db=db,
            id=receipt_id,
            user_id=user_id,
            name=name,
            file_path=str(output_path)
        )

        # 문서 반환
        return FileResponse(
            path=output_path,
            filename=f"{receipt_id}_expense_report.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    except Exception as e:
        return {"error": str(e)}
    finally:
        # 임시 파일 정리
        for path in image_paths:
            try:
                os.remove(path)
            except:
                pass
        try:
            if json_path.exists():
                os.remove(json_path)
        except:
            pass


@router.get("/download")
async def download_report(receipt_id: str = Query(...)):
    """생성된 문서를 다운로드합니다."""
    output_path = Path("output") / f"{receipt_id}_expense_report.docx"

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="문서가 존재하지 않습니다.")

    return FileResponse(
        path=output_path,
        filename=f"{receipt_id}_expense_report.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

@router.get("/my/{user_id}")
async def get_receipts_by_user_id(user_id: str, db: AsyncSession = Depends(get_db)):
    """유저 ID로 영수증 조회"""
    try:
        receipts = await get_my_receipts(db, user_id)
        if receipts:
            return receipts
        else:
            return {"message": "No receipts found for this user"}, 404
    except Exception as e:
        return {"message": "Internal server error"}, 500