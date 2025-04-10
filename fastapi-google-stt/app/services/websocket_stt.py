# services/speech_service.py
import os
import json
import logging
from dotenv import load_dotenv
from fastapi import WebSocket
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types

# 환경 변수 로드
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")

async def handle_websocket_connection(websocket: WebSocket):
    """
    WebSocket 연결을 처리하는 함수
    
    Args:
        websocket (WebSocket): 연결된 WebSocket 객체
    """
    # 상태 관리 변수
    is_active = False
    language_code = "ko-KR"  # 기본 언어
    audio_buffer = bytearray()
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            message = await websocket.receive()
            
            # 텍스트 메시지인 경우 (명령 처리)
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type")
                    
                    if msg_type == "start":
                        # 녹음 시작 명령
                        language_code = data.get("lang", "ko-KR")
                        is_active = True
                        audio_buffer = bytearray()  # 버퍼 초기화
                        await websocket.send_text(f"인식 시작: 언어 - {language_code}")
                        logging.info(f"음성 인식 시작: 언어 - {language_code}")
                        
                    elif msg_type == "end":
                        # 녹음 종료 명령
                        is_active = False
                        
                        # 버퍼에 음성이 있으면 마지막으로 처리
                        if audio_buffer:
                            async for transcript in transcribe_streaming(bytes(audio_buffer), language_code):
                                await websocket.send_text(transcript)
                            audio_buffer = bytearray()  # 버퍼 초기화
                            
                        await websocket.send_text("인식 종료: 다음 세션 대기 중")
                        logging.info("음성 인식 종료, 다음 세션 대기 중")
                        # 세션을 종료하지 않고 다음 start 메시지 대기
                        
                except json.JSONDecodeError:
                    logging.error("잘못된 JSON 형식")
                    
            # 바이너리 메시지인 경우 (오디오 데이터)
            elif "bytes" in message and is_active:
                audio_chunk = message["bytes"]
                
                # 오디오 버퍼에 추가
                audio_buffer.extend(audio_chunk)
                
                # 충분한 데이터가 모이면 처리 (약 0.5-1초 분량)
                if len(audio_buffer) > 2000:  # 8KB 임계값 (조정 가능)
                    async for transcript in transcribe_streaming(bytes(audio_buffer), language_code):
                        await websocket.send_text(transcript)
                    audio_buffer = bytearray()  # 처리 후 버퍼 초기화
                
    except Exception as e:
        logging.error(f"WebSocket 오류: {str(e)}")

async def transcribe_streaming(audio_content: bytes, language_code: str = "ko-KR"):
    """
    오디오 바이트를 받아 Google Cloud Speech-to-Text API를 사용하여 음성을 텍스트로 변환하고,
    스트리밍 방식으로 결과를 반환합니다.
    
    Args:
        audio_content (bytes): 변환할 오디오 데이터 바이트
        language_code (str): 음성 인식 언어 코드 (기본값: "ko-KR")
        
    Yields:
        str: 변환된 텍스트 조각
    """
    try:
        # if not audio_content or len(audio_content) < 100:  # 너무 짧은 오디오는 처리하지 않음
        #     return
            
        client = SpeechClient()
        
        # 데이터를 청크로 나눔
        chunk_length = len(audio_content) // 10
        if chunk_length <= 0:
            chunk_length = len(audio_content)
            
        stream = [
            audio_content[start : start + chunk_length]
            for start in range(0, len(audio_content), chunk_length)
        ]
        
        audio_requests = (
            cloud_speech_types.StreamingRecognizeRequest(audio=audio) 
            for audio in stream
        )
        
        # 음성 인식 설정
        recognition_config = cloud_speech_types.RecognitionConfig(
            auto_decoding_config=cloud_speech_types.AutoDetectDecodingConfig(),
            language_codes=[language_code],  # 동적으로 언어 설정
            model="long",
        )
        
        streaming_config = cloud_speech_types.StreamingRecognitionConfig(
            config=recognition_config
        )
        
        config_request = cloud_speech_types.StreamingRecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
            streaming_config=streaming_config,
        )
        
        def requests(config, audio):
            yield config
            yield from audio
        
        # Google STT API 호출
        responses_iterator = client.streaming_recognize(
            requests=requests(config_request, audio_requests)
        )

        # # 스트리밍 방식으로 응답 반환
        for response in responses_iterator:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                yield f"data: {transcript}\n\n"
                
    except Exception as e:
        logging.error(f"Speech-to-Text 에러: {str(e)}")
        yield f"음성 인식 오류: {str(e)}"