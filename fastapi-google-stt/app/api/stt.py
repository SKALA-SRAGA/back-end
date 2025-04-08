from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from app.services.google_stt import transcribe_streaming_v2

router = APIRouter()

@router.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
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