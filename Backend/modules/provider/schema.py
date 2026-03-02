from pydantic import BaseModel
from typing import List, Optional

class ModelInfo(BaseModel):
    provider: str
    id: str
    name: str

class AvailableModelOption(BaseModel):
    id: str
    name: str
    description: str
    provider: str
    is_chat_model: bool
    is_inference_model: bool

class ProviderInfo(BaseModel):
    id: str
    name: str
    description: str

class GetProviderResponse(BaseModel):
    chat_model: ModelInfo
    inference_model: ModelInfo

class AvailableModelsResponse(BaseModel):
    models: List[AvailableModelOption]

class SetProviderRequest(BaseModel):
    chat_model: Optional[str] = None
    inference_model: Optional[str] = None
