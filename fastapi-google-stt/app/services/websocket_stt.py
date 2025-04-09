import asyncio
import uuid
import logging
from typing import Dict, List
from fastapi import WebSocket
from google.cloud import speech
import ffmpeg

# 로깅 설정
logger = logging.getLogger(__name__)

# 글로벌 변수
speech_client = None
lang = "ko-KR"
active_connections: Dict[str, WebSocket] = {}
audio_buffers: Dict[str, List[bytes]] = {}
processing_tasks: Dict[str, asyncio.Task] = {}

def initialize_service():
    """Google STT 서비스 초기화"""
    global speech_client
    try:
        speech_client = speech.SpeechClient()
        logger.info("Google Speech-to-Text 클라이언트가 초기화되었습니다")
    except Exception as e:
        logger.error(f"Google STT 클라이언트 초기화 오류: {str(e)}")
        raise

async def handle_websocket_connection(websocket: WebSocket, target_lang: str):
    global lang
    """WebSocket 연결을 처리하고 오디오 처리 태스크를 시작"""
    # 연결 수락
    await websocket.accept()

    lang = target_lang
    
    # 연결 ID 생성
    connection_id = str(uuid.uuid4())
    active_connections[connection_id] = websocket
    audio_buffers[connection_id] = []
    
    logger.info(f"새 WebSocket 연결 설정: {connection_id}")
    
    # 연결 상태 전송
    await websocket.send_json({
        "type": "connection_status",
        "status": "connected",
        "connection_id": connection_id
    })
    
    # 오디오 처리 태스크 시작
    task = asyncio.create_task(process_audio_buffer(connection_id))
    processing_tasks[connection_id] = task
    
    try:
        # 클라이언트로부터 오디오 데이터 수신
        while True:
            audio_chunk = await websocket.receive_bytes()
            add_audio_chunk(connection_id, audio_chunk)
    finally:
        # 연결 종료 시 정리
        await cleanup_connection(connection_id)

async def cleanup_connection(connection_id: str):
    """연결 종료 시 리소스 정리"""
    if connection_id in processing_tasks:
        processing_tasks[connection_id].cancel()
        del processing_tasks[connection_id]
    
    if connection_id in active_connections:
        del active_connections[connection_id]
    
    if connection_id in audio_buffers:
        del audio_buffers[connection_id]
    
    logger.info(f"연결 종료 및 정리 완료: {connection_id}")

def add_audio_chunk(connection_id: str, chunk: bytes):
    """오디오 버퍼에 청크 추가"""
    if connection_id in audio_buffers:
        audio_buffers[connection_id].append(chunk)

def get_and_clear_audio_buffer(connection_id: str) -> List[bytes]:
    """오디오 버퍼를 가져오고 비움"""
    if connection_id in audio_buffers:
        buffer = audio_buffers[connection_id].copy()
        audio_buffers[connection_id] = []
        return buffer
    return []

async def process_audio_buffer(connection_id: str):
    """주기적으로 오디오 버퍼를 처리하고 STT API 호출"""
    websocket = active_connections.get(connection_id)
    if not websocket:
        return

    while True:
        try:
            # 버퍼에서 오디오 청크 수집
            audio_chunks = get_and_clear_audio_buffer(connection_id)
            
            if not audio_chunks:
                await asyncio.sleep(0.1)  # 버퍼가 비어있으면 대기
                continue
            
            # WebM 데이터를 합치고 WAV로 변환
            audio_data = b''.join(audio_chunks)
            if not audio_data:
                continue

            if len(audio_data) < 500:  # 최소 500 바이트 이상인 데이터만 처리
                continue
                
            wav_audio = convert_webm_to_wav(audio_data)
            
            # Google STT API 호출
            text = transcribe_audio(wav_audio, lang)

            await websocket.send_json({
                "type": "status",
                "status": "processing",
                "message": "Processing audio data..."
            })
            
            if text:
                await websocket.send_json({"type": "transcription", "text": text})
            
            await asyncio.sleep(0.1)  # 처리 간격
            
        except asyncio.CancelledError:
            logger.info(f"오디오 처리 태스크 취소됨: {connection_id}")
            break
        except Exception as e:
            logger.error(f"오디오 처리 오류: {str(e)}")
            await asyncio.sleep(1)  # 오류 발생 시 잠시 대기

def convert_webm_to_wav(webm_data: bytes) -> bytes:
    """WebM 오디오를 WAV 형식으로 변환"""
    try:
        process = (
            ffmpeg
            .input('pipe:0', format='webm')
            .output('pipe:1', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )
        
        stdout_data, stderr_data = process.communicate(input=webm_data)
        
        if process.returncode != 0:
            logger.error(f"FFmpeg 오류: {stderr_data.decode()}")
            return b''
            
        return stdout_data
        
    except Exception as e:
        logger.error(f"WebM에서 WAV 변환 오류: {str(e)}")
        return b''

def transcribe_audio(audio_data: bytes, language_code: str = "ko-KR") -> str:
    """Google Speech-to-Text API를 사용하여 오디오를 텍스트로 변환"""
    global speech_client

    print("Transcribing Audio..")  # 디버깅용 로그
    
    if not audio_data or not speech_client:
        return ""
        
    try:
        audio = speech.RecognitionAudio(content=audio_data)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        response = speech_client.recognize(config=config, audio=audio)
        
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
            
        return transcript
        
    except Exception as e:
        logger.error(f"음성 인식 오류: {str(e)}")
        return ""