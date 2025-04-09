from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_teddynote.messages import stream_response
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model="gpt-4o", temperature=0.5, max_tokens=1024)
templete='{text}을 한국어로 번역해주세요. 번역 된 문장만 출력해주세요.'
prompt = PromptTemplate.from_template(templete)
output_parser = StrOutputParser()
chain = prompt | model | output_parser

def get_streaming_message_from_openai(data: str):
    try:
        # 스트리밍 응답 생성
        response = chain.stream(data)
        # stream_response(response)

        for token in response:
            print(f"Token: {token}")
        print("data: [DONE]\n\n")
    except Exception as e:
        # 에러 발생 시 스트리밍 방식으로 에러 메시지 반환
        print(f"[Error: {str(e)}]")

get_streaming_message_from_openai("The learning principle of an AI model is a process of adjusting internal weights using input data so that it can produce the desired output.")