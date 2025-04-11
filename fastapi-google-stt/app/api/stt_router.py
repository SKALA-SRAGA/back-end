import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import StreamingResponse
from app.services.google_stt_service import transcribe_streaming_v2
from app.services.websocket_stt_service import handle_websocket_connection

router = APIRouter()

# 로깅 설정
logger = logging.getLogger(__name__)

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    ## 오디오 파일 전송 및 STT 결과 변환 - SSE 스트리밍 방식
    - file: mp3, wav, ogg 등 오디오 파일
    """
    try:
        print(f"File type: {type(file)}")  # 디버깅용 로그
        print(f"File name: {file.filename}")  # 파일 이름 확인


        audio_content = await file.read()  # 파일 내용을 비동기적으로 읽음

        # StreamingResponse를 사용하여 스트리밍 방식으로 데이터 반환
        return StreamingResponse(
            transcribe_streaming_v2(audio_content), media_type="text/event-stream"
        )

    except Exception as e:
        return StreamingResponse(
            (f"data: [Error: {str(e)}]\n\n" for _ in range(1)),  # 에러 메시지를 스트리밍 방식으로 반환
            media_type="text/event-stream",
            status_code=500,
        )

# @router.websocket("/websocket/")
# async def websocket_stt(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket connection accepted")
#     await websocket_streaming(websocket)

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