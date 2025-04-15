import base64
from PIL import Image
import requests
import io
import os
import json
import re
import uuid

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from PIL import Image

from app.db.entity.receipt import Receipt
from app.db.repository.receipt_repository import (
    create,
    find_receipt_by_user_id,
)
from app.dto.receipt_response import ReceiptResponse

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def create_receipt(db: AsyncSession, 
                        id=str,
                        user_id = int, 
                        name = str, 
                        file_path = str):
    """
    영수증을 생성하는 함수
    """
    receipt = Receipt(id=id, user_id=user_id, name=name, file_path=file_path)
    await create(db, receipt)

async def get_my_receipts(db: AsyncSession, user_id: int) -> list:
    """
    user_id로 영수증을 조회하는 함수
    """
    receipts = await find_receipt_by_user_id(db, user_id)

    # Receipt 객체를 ReceiptIdResponse로 변환
    return [ReceiptResponse(id=receipt.id, name=receipt.name) for receipt in receipts]

# 이미지 인코딩 함수
def resize_and_encode_image(image_path: str, max_width: int = 300) -> str:
    img = Image.open(image_path)

    # RGBA → RGB 변환 (투명도 제거)
    if img.mode == "RGBA":
        img = img.convert("RGB")

    # 리사이징
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size)

    # 버퍼에 저장
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=80)

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def get_image_description(image_path, llm_instance):

    image = resize_and_encode_image(image_path)

    photo_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                당신의 역할은 사용자가 업로드한 영수증 이미지를 분석하여, 출장 경비 정산 문서를 생성하기 위한 정보를 JSON로 정리하는 것입니다.
                
                **요구 사항**:
                - 이미지 속 날짜, 항목명(식비, 교통비, 숙박비, 기타), 지출처(상호명), 금액, 통화 정보를 추출합니다.
                - 다음과 같은 JSON 형식을 따르세요:

                    ```json
                    [
                    {{
                        "category": "식비",            // 항목: 교통비, 식비, 숙박비, 기타 중 하나
                        "vendor": "스타벅스",         // 상호명 또는 지출처 (영수증 바탕으로로)
                        "vendor_kor" : "스타벅스", // 상호명 또는 지출처 (한글)
                        "details": "아메리카노",        // 상세 내역 (영수증 바탕으로 "음료", "식사" 등 **포괄적으로** 한글로 작성)
                        "currency": "KRW",           // 현지 통화 (예: KRW, JPY, USD 등)
                        "amount": 8200,              // 현지 금액 (숫자만)
                        "date": "2024-04-10"         // 사용 날짜 (YYYY-MM-DD) 
                    }}
                    ]
                
                **제약 사항**:
                - 날짜는 다양한 형식으로 나타날 수 있습니다. 
                    예시:
                        - "13JUN '17", "06/13/2017", "2017.06.13", "17-06-23", "13 JUN 2017", "JUN 13 2017" 등
                        - 모든 날짜는 반드시 `YYYY-MM-DD` 형식으로 변환해야 합니다.
                """,
            ),
            ("user", [{"type": "image_url", "image_url": {"url": image}}]),
        ]
    )
    chain = photo_prompt | llm_instance | StrOutputParser()
    result = chain.invoke({"image": image})
    return result


# 여러 이미지 처리 함수
def process_multiple_images(image_paths: list) -> list:

    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model="gpt-4o",
        temperature=0,
    )

    results = []
    for path in image_paths:
        print(f"처리 중: {os.path.basename(path)}")
        try:
            raw_result = get_image_description(path, llm)

            # ```json ~ ``` 제거
            json_text = re.sub(r"```json|```", "", raw_result).strip()

            # JSON 파싱
            parsed = json.loads(json_text)

            results.append({"file": os.path.basename(path), "result": parsed})
        except Exception as e:
            results.append({"file": os.path.basename(path), "error": str(e)})
    return results

def generate_base64_uuid():
    uuid_bytes = uuid.uuid4().bytes
    return base64.urlsafe_b64encode(uuid_bytes).decode('utf-8').rstrip('=')