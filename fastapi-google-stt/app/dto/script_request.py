from pydantic import BaseModel, ConfigDict

class CreateScriptRequest(BaseModel):
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)