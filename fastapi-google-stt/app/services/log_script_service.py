from app.db.repository.script_repository import (
    find_script_by_id,
    find_script_by_user_id,
    create_script,
    update_script,
    delete_script,
)

import io
import os
import uuid
import base64

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.entity.script import Script
from app.dto.message_request import MessageRequest
from app.dto.script_id_reponse import ScriptIdResponse

speacker = None
file = None

load_dotenv()

PATH = os.getenv("SCRIPT_PATH")

async def create(db: AsyncSession, user_id: int) -> ScriptIdResponse:
    """
    스크립트를 생성하는 함수
    """
    id = generate_base64_uuid()
    file_path = PATH + "/" + id + ".txt"
    script = Script(id=id, user_id=user_id, file_path=file_path)
    
    await create_script(db, script)

    return ScriptIdResponse(id=id)

async def get_scripts_by_user_id(db: AsyncSession, user_id: int) -> list | None:
    """
    id로 스크립트를 조회하는 함수
    """
    scripts = await find_script_by_user_id(db, user_id)

    # Script 객체를 ScriptIdResponse로 변환
    return [ScriptIdResponse(id=script.id) for script in scripts]

async def get_script_by_id(db: AsyncSession, script_id: str) -> Script | None:
    """
    id로 스크립트를 조회하는 함수
    """
    script = await find_script_by_id(db, script_id)

    if not script:
        raise ValueError(f"Script with ID {script_id} not found")

    # 파일 경로 가져오기
    file_path = script.file_path

    # 파일 내용 읽기
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()  # 파일 내용 반환
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {str(e)}")
    else:
        raise FileNotFoundError(f"File not found at path: {file_path}")

async def logger(db: AsyncSession, data: MessageRequest, script_id: str):
    """
    로그를 파일에 저장하고, 파일의 내용을 반환하는 함수
    - db: 데이터베이스 세션
    - data: MessageRequest 객체 (message 필드 포함)
    - script_id: 스크립트 ID
    """
    # script_id로 스크립트 조회
    script = await find_script_by_id(db, script_id)
    if not script:
        raise ValueError(f"Script with ID {script_id} not found")

    # 파일 경로 가져오기
    file_path = script.file_path

    # 파일이 없으면 새로 생성
    if not os.path.exists(file_path):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 디렉토리 생성
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("")  # 빈 파일 생성
        except Exception as e:
            raise IOError(f"Failed to create file {file_path}: {str(e)}")

    # 파일에 메시지 저장
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(data.message + "\n")  # 메시지를 파일에 추가
    except Exception as e:
        raise IOError(f"Failed to write to file {file_path}: {str(e)}")

def generate_base64_uuid():
    uuid_bytes = uuid.uuid4().bytes
    return base64.urlsafe_b64encode(uuid_bytes).decode('utf-8').rstrip('=')