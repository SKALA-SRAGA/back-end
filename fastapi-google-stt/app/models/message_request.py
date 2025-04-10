from pydantic import BaseModel

class MessageRequest(BaseModel):
    lang: str
    message: str