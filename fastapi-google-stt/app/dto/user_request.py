from pydantic import BaseModel, ConfigDict

class CreateUserRequest(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class UpdateUserRequest(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)