from pydantic import BaseModel, ConfigDict

class ScriptResponse(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)