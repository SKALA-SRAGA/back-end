# services/speech_service.py
import os
import json
import logging
import asyncio
import threading
import queue
from dotenv import load_dotenv
from fastapi import WebSocket
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types
from app.services.openai_vector_store import add_text

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

    # 스레드 간 데이터 교환을 위한 큐
    audio_queue = queue.Queue()
    response_queue = asyncio.Queue()
    
    # STT 스트리밍 스레드
    stt_thread = None
    
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
                        # 이전 스레드가 실행 중이면 종료
                        if stt_thread and stt_thread.is_alive():
                            audio_queue.put(None)  # 종료 신호
                            stt_thread.join(timeout=2)
                            
                        # 큐 초기화
                        while not audio_queue.empty():
                            audio_queue.get()
                        while not response_queue.empty():
                            await response_queue.get()
                        
                        # 녹음 시작 명령
                        language_code = data.get("lang", "ko-KR")
                        is_active = True
                        
                        await websocket.send_text(json.dumps({
                            "type": "system",
                            "message": f"인식 시작: 언어 - {language_code}"
                        }, ensure_ascii=False))
                        
                        logging.info(f"음성 인식 시작: 언어 - {language_code}")
                        
                        # 새로운 STT 스레드 시작
                        stt_thread = threading.Thread(
                            target=run_stt_stream,
                            args=(audio_queue, response_queue, language_code)
                        )
                        stt_thread.daemon = True
                        stt_thread.start()
                        
                        # 응답 처리 태스크 시작
                        asyncio.create_task(process_responses(response_queue, websocket))
                        
                    elif msg_type == "end":
                        # 녹음 종료 명령
                        is_active = False
                        
                        # 스트리밍 종료 신호
                        audio_queue.put(None)
                        
                        # await websocket.send_text(json.dumps({
                        #     "type": "system",
                        #     "message": "인식 종료: 다음 세션 대기 중"
                        # }, ensure_ascii=False))
                        
                        logging.info("음성 인식 종료, 다음 세션 대기 중")
                        
                except json.JSONDecodeError:
                    logging.error("잘못된 JSON 형식")
                    
            # 바이너리 메시지인 경우 (오디오 데이터)
            elif "bytes" in message and is_active:
                audio_chunk = message["bytes"]
                # 오디오 데이터를 큐에 추가
                audio_queue.put(audio_chunk)
                
    except Exception as e:
        logging.error(f"WebSocket 오류: {str(e)}")
        # 스레드 정리
        if stt_thread and stt_thread.is_alive():
            audio_queue.put(None)  # 종료 신호

def run_stt_stream(audio_queue, response_queue, language_code):
    """
    별도 스레드에서 STT 스트리밍을 실행하는 함수
    
    Args:
        audio_queue (queue.Queue): 오디오 데이터를 받는 큐
        response_queue (asyncio.Queue): 처리 결과를 전달할 큐
        language_code (str): 인식 언어 코드
    """
    try:
        client = SpeechClient()
        
        # 음성 인식 설정
        recognition_config = cloud_speech_types.RecognitionConfig(
            explicit_decoding_config=cloud_speech_types.ExplicitDecodingConfig(
                encoding=cloud_speech_types.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                audio_channel_count=1,
            ),
            language_codes=[language_code],
            model="long",
        )

        streaming_features = cloud_speech_types.StreamingRecognitionFeatures(
            interim_results=True,
        )
        
        streaming_config = cloud_speech_types.StreamingRecognitionConfig(
            config=recognition_config,
            streaming_features=streaming_features,
        )
        
        config_request = cloud_speech_types.StreamingRecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
            streaming_config=streaming_config,
        )
        
        # 동기 제너레이터 - STT API 호출에 사용
        def request_generator():
            # 설정 요청 먼저 보내기
            yield config_request
            
            while True:
                # 큐에서 오디오 데이터 가져오기 (blocking)
                chunk = audio_queue.get()
                
                # None은 스트림 종료 신호
                if chunk is None:
                    break
                    
                # 오디오 데이터 요청 생성 및 전송
                yield cloud_speech_types.StreamingRecognizeRequest(audio=chunk)
        
        # Google STT API 호출
        responses = client.streaming_recognize(requests=request_generator())
        
        # 응답 처리 및 결과 큐에 추가
        for response in responses:
            # 결과가 없는 경우 스킵
            if not response.results:
                continue
                
            # 마지막 결과만 처리 (일반적으로 가장 최신, 가장 정확한 결과)
            result = response.results[-1]
            
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                is_final = result.is_final
                confidence = result.alternatives[0].confidence if hasattr(result.alternatives[0], 'confidence') else 0.0
                
                # 메인 스레드에 응답 전달
                asyncio.run(response_queue.put({
                    "transcript": transcript,
                    "is_final": is_final,
                    "confidence": confidence,
                }))
        
    except Exception as e:
        logging.error(f"STT 스트리밍 오류: {str(e)}")
        # 오류 정보 전달
        try:
            asyncio.run(response_queue.put({
                "error": str(e)
            }))
        except:
            pass

async def process_responses(response_queue, websocket):
    """
    STT 응답을 처리하고 WebSocket으로 전송하는 함수
    중간 결과는 'interim' 타입으로, 최종 결과는 'final' 타입으로 전송합니다.
    
    Args:
        response_queue (asyncio.Queue): STT 결과를 받는 큐
        websocket (WebSocket): 결과를 전송할 WebSocket
    """
    # 현재 상태 관리
    last_interim_text = ""  # 마지막으로 전송한 중간 텍스트
    last_final_text = ""    # 마지막으로 전송한 최종 텍스트
    
    try:
        while True:
            # 큐에서 응답 가져오기
            response = await response_queue.get()
            
            # 오류 발생 시
            if "error" in response:
                error_response = {
                    "type": "error",
                    "message": f"음성 인식 오류: {response['error']}"
                }
                await websocket.send_text(json.dumps(error_response, ensure_ascii=False))
                continue
                
            # 정상 응답 처리
            transcript = response["transcript"].strip()
            is_final = response["is_final"]
            # confidence = response.get("confidence", 0.0)
            
            # 텍스트가 비어있으면 무시
            if not transcript:
                continue
                
            # 결과 유형에 따라 처리
            if is_final:
                # 최종 결과가 이전 최종 결과와 다를 경우에만 전송
                if transcript != last_final_text:
                    json_response = {
                        "type": "final",
                        "text": transcript,
                        # "confidence": confidence
                    }
                    await websocket.send_text(json.dumps(json_response, ensure_ascii=False))
                    last_final_text = transcript

                # 중간 결과 초기화
                last_interim_text = ""
                
            else:
                # 중간 결과가 이전 중간 결과와 다를 경우에만 전송
                if transcript != last_interim_text:
                    json_response = {
                        "type": "interim",
                        "text": transcript,
                        # "confidence": confidence
                    }
                    await websocket.send_text(json.dumps(json_response, ensure_ascii=False))
                    last_interim_text = transcript
                    
    except asyncio.CancelledError:
        # 태스크 취소
        return
    except Exception as e:
        logging.error(f"응답 처리 오류: {str(e)}")
        error_response = {
            "type": "error",
            "message": f"응답 처리 오류: {str(e)}"
        }
        await websocket.send_text(json.dumps(error_response, ensure_ascii=False))

