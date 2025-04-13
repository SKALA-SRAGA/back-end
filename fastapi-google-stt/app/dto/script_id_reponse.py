from pydantic import BaseModel, ConfigDict

class ScriptIdResponse(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)