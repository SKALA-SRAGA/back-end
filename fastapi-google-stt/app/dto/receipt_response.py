from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReceiptResponse(BaseModel):
    id: str
    created_date: datetime
    name: str

    model_config = ConfigDict(from_attributes=True)