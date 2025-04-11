import io
from app.dto.message_request import MessageRequest

speacker = None
file = None

def logger(data: MessageRequest, x_user_id: str = None):
    """
    로그를 파일에 저장하는 함수
    """

    if speacker is None and file is None:
        speacker = "a"
        file = io.StringIO()
        
    return "file path"