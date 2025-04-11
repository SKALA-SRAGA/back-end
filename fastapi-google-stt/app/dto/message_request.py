from pydantic import BaseModel, ConfigDict

class MessageRequest(BaseModel):
    lang: str
    message: str

    model_config = ConfigDict(from_attributes=True)