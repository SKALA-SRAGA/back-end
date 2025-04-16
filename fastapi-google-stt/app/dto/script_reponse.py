from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ScriptResponse(BaseModel):
    id: str
    created_date: datetime
    name: str

    model_config = ConfigDict(from_attributes=True)