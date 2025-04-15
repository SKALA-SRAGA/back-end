from pydantic import BaseModel, ConfigDict

class AskRequest(BaseModel):
    script_id: str
    query: str

    model_config = ConfigDict(from_attributes=True)