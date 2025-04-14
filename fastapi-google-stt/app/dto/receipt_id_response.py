from pydantic import BaseModel, ConfigDict

class ReceiptIdResponse(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)