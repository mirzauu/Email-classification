import os
import random
import asyncio
import time
import logging
from typing import List, Dict, Any, Union, AsyncGenerator, Optional
from functools import wraps
from pydantic import BaseModel

# Try to import litellm and instructor
try:
    import litellm
    from litellm import acompletion
    import instructor
    from openai import AsyncOpenAI
except ImportError:
    # We will assume these are installed or will be installed
    litellm = None
    acompletion = None
    instructor = None
    AsyncOpenAI = None

from core.config import settings
from modules.users.models import UserPreferences
from .schema import (
    ProviderInfo,
    GetProviderResponse,
    AvailableModelsResponse,
    AvailableModelOption,
    SetProviderRequest,
    ModelInfo,
)
from .llm_config import (
    LLMProviderConfig,
    LLMConfigManager,
    DEFAULT_CHAT_MODEL,
    DEFAULT_INFERENCE_MODEL,
)
from .exceptions import UnsupportedProviderError

logger = logging.getLogger(__name__)

# Available models with their metadata
AVAILABLE_MODELS = [
    AvailableModelOption(
        id="openai/gpt-5.2",
        name="GPT-5.2",
        description="OpenAI's latest model for complex tasks",
        provider="openai",
        is_chat_model=True,
        is_inference_model=False,
    ),
    AvailableModelOption(
        id="openai/gpt-5-mini",
        name="GPT-5 Mini",
        description="Smaller model for fast tasks",
        provider="openai",
        is_chat_model=False,
        is_inference_model=True,
    ),
    AvailableModelOption(
        id="anthropic/claude-3-7-sonnet-20250219",
        name="Claude Sonnet 3.7",
        description="Highest level of intelligence",
        provider="anthropic",
        is_chat_model=True,
        is_inference_model=False,
    ),
    # Add other models as needed...
]

class RetrySettings:
    """Configuration class for retry behavior"""
    def __init__(
        self,
        max_retries: int = 8,
        min_delay: float = 1.0,
        max_delay: float = 120.0,
        base_delay: float = 2.0,
        jitter_factor: float = 0.2,
        step_increase: float = 1.8,
    ):
        self.max_retries = max_retries
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.base_delay = base_delay
        self.jitter_factor = jitter_factor
        self.step_increase = step_increase

class LLMUtils:
    @staticmethod
    def identify_provider_from_error(error: Exception) -> str:
        error_str = str(error).lower()
        for provider in ["anthropic", "openai", "cohere", "azure"]:
            if provider.lower() in error_str:
                return provider
        return "unknown"

    @staticmethod
    def is_recoverable_error(error: Exception) -> bool:
        error_str = str(error).lower()
        recoverable_patterns = [
            "timeout", "overloaded", "capacity", "rate limit", 
            "500", "502", "503", "504", "server_error"
        ]
        return any(pattern in error_str for pattern in recoverable_patterns)

    @staticmethod
    def calculate_backoff_time(retry_count: int, settings: RetrySettings) -> float:
        delay = min(
            settings.max_delay, 
            settings.base_delay * (settings.step_increase ** retry_count)
        )
        jitter = random.uniform(1 - settings.jitter_factor, 1 + settings.jitter_factor)
        return max(settings.min_delay, min(settings.max_delay, delay * jitter))

    @staticmethod
    def sanitize_messages_for_tracing(messages: list) -> list:
        sanitized = []
        for msg in messages:
            if isinstance(msg, dict):
                s_msg = msg.copy()
                if "content" in s_msg and s_msg["content"] is None:
                    s_msg["content"] = ""
                sanitized.append(s_msg)
            else:
                sanitized.append(msg)
        return sanitized

def robust_llm_call(settings: Optional[RetrySettings] = None):
    if settings is None:
        settings = RetrySettings()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries <= settings.max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if not LLMUtils.is_recoverable_error(e) or retries >= settings.max_retries:
                        raise e
                    
                    delay = LLMUtils.calculate_backoff_time(retries, settings)
                    logger.warning(f"Retry {retries + 1}/{settings.max_retries} after {delay:.2f}s due to: {e}")
                    await asyncio.sleep(delay)
                    retries += 1
        return wrapper
    return decorator

class ProviderService:
    def __init__(self, db, user_id: str):
        if litellm:
            litellm.modify_params = True
        self.db = db
        self.user_id = user_id
        self._api_key_cache: Dict[str, Optional[str]] = {}

        # Load user preferences
        user_pref = db.query(UserPreferences).filter_by(user_id=user_id).first()
        user_config = user_pref.preferences if user_pref and user_pref.preferences else {}

        self.chat_config = LLMConfigManager.build_llm_provider_config(user_config, "chat")
        self.inference_config = LLMConfigManager.build_llm_provider_config(user_config, "inference")
        self.retry_settings = RetrySettings()

    @classmethod
    def create(cls, db, user_id: str):
        return cls(db, user_id)

    async def list_available_models(self) -> AvailableModelsResponse:
        return AvailableModelsResponse(models=AVAILABLE_MODELS)

    async def set_global_ai_provider(self, request: SetProviderRequest):
        preferences = self.db.query(UserPreferences).filter_by(user_id=self.user_id).first()
        if not preferences:
            preferences = UserPreferences(user_id=self.user_id, preferences={})
            self.db.add(preferences)
        
        updated_prefs = (preferences.preferences or {}).copy()
        if request.chat_model:
            updated_prefs["chat_model"] = request.chat_model
        if request.inference_model:
            updated_prefs["inference_model"] = request.inference_model
        
        preferences.preferences = updated_prefs
        self.db.commit()
        return {"message": "AI configuration updated"}

    def _get_api_key(self, provider: str) -> Optional[str]:
        if provider in self._api_key_cache:
            return self._api_key_cache[provider]
        
        # Simple env-based key retrieval
        key = os.getenv(f"{provider.upper()}_API_KEY") or os.getenv("LLM_API_KEY")
        self._api_key_cache[provider] = key
        return key

    def _build_llm_params(self, config: LLMProviderConfig) -> Dict[str, Any]:
        api_key = self._get_api_key(config.auth_provider)
        params = config.get_llm_params(api_key)
        if config.base_url:
            params["base_url"] = config.base_url
        if config.api_version:
            params["api_version"] = config.api_version
        return {k: v for k, v in params.items() if v is not None}

    @robust_llm_call()
    async def call_llm(self, messages: list, stream: bool = False, config_type: str = "chat") -> Union[str, AsyncGenerator[str, None]]:
        messages = LLMUtils.sanitize_messages_for_tracing(messages)
        config = self.chat_config if config_type == "chat" else self.inference_config
        params = self._build_llm_params(config)

        if stream:
            async def generator():
                response = await acompletion(messages=messages, stream=True, **params)
                async for chunk in response:
                    yield chunk.choices[0].delta.content or ""
            return generator()
        else:
            response = await acompletion(messages=messages, **params)
            return response.choices[0].message.content

    @robust_llm_call()
    async def call_llm_with_structured_output(self, messages: list, output_schema: Any, config_type: str = "chat") -> Any:
        messages = LLMUtils.sanitize_messages_for_tracing(messages)
        config = self.chat_config if config_type == "chat" else self.inference_config
        params = self._build_llm_params(config)

        client = instructor.from_litellm(acompletion, mode=instructor.Mode.JSON)
        return await client.chat.completions.create(
            model=params["model"],
            messages=messages,
            response_model=output_schema,
            **{k: v for k, v in params.items() if k not in ["model"]}
        )
