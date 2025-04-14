import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import StreamingResponse
from app.services.google_stt_service import transcribe_streaming_v2
from app.services.websocket_stt_service import handle_websocket_connection

router = APIRouter()

# 로깅 설정
logger = logging.getLogger(__name__)

@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket):
    """
    ## 웹소켓으로 오디오 파일 전송 및 실시간 STT 결과 변환
    """
    try:
        # 웹소켓 연결 및 처리 로직은 websocket_stt.py로 위임
        await websocket.accept()
        await handle_websocket_connection(websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket 연결이 종료되었습니다")
    except Exception as e:
        logger.error(f"WebSocket 오류: {str(e)}")