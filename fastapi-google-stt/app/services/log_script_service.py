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

def logger(data: MessageRequest, x_user_id: str = None):
    """
    로그를 파일에 저장하는 함수
    """

    if speacker is None and file is None:
        speacker = "a"
        file = io.StringIO()
        
    return "file path"


def generate_base64_uuid():
    uuid_bytes = uuid.uuid4().bytes
    return base64.urlsafe_b64encode(uuid_bytes).decode('utf-8').rstrip('=')