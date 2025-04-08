import os
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types

PROJECT_ID = os.getenv("PROJECT_ID")

async def transcribe_streaming_v2(audio_content: bytes):
    client = SpeechClient()

    # 데이터를 청크로 나눔
    chunk_length = len(audio_content) // 5
    stream = [
        audio_content[start : start + chunk_length]
        for start in range(0, len(audio_content), chunk_length)
    ]
    audio_requests = (
        cloud_speech_types.StreamingRecognizeRequest(audio=audio) for audio in stream
    )

    recognition_config = cloud_speech_types.RecognitionConfig(
        auto_decoding_config=cloud_speech_types.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
    )
    streaming_config = cloud_speech_types.StreamingRecognitionConfig(
        config=recognition_config
    )
    config_request = cloud_speech_types.StreamingRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        streaming_config=streaming_config,
    )

    def requests(config: cloud_speech_types.RecognitionConfig, audio: list):
        yield config
        yield from audio

    # Google STT API 호출
    responses_iterator = client.streaming_recognize(
        requests=requests(config_request, audio_requests)
    )

    # 스트리밍 방식으로 응답 반환
    for response in responses_iterator:
        for result in response.results:
            transcript = result.alternatives[0].transcript
            yield f"data: {transcript}\n\n"  # EventStream 형식으로 반환