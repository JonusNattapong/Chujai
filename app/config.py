import os
from typing import Dict, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class MistralConfig(BaseSettings):
    """Mistral AI specific configuration."""
    api_key: Optional[str] = Field(None, env="MISTRAL_API_KEY")
    api_base: str = Field("https://api.mistral.ai/v1", env="MISTRAL_API_BASE")
    default_model: str = Field("mistral-medium", env="MISTRAL_DEFAULT_MODEL")
    
    # Default parameters
    max_tokens: Optional[int] = Field(None, env="MISTRAL_MAX_TOKENS")
    temperature: float = Field(0.7, env="MISTRAL_TEMPERATURE")
    top_p: Optional[float] = Field(None, env="MISTRAL_TOP_P")
    safe_mode: bool = Field(False, env="MISTRAL_SAFE_MODE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class APIConfig(BaseSettings):
    """API configuration settings."""
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    mistral_api_key: Optional[str] = Field(None, env="MISTRAL_API_KEY")
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    
    # API base URLs (can be overridden for custom endpoints)
    openai_api_base: str = Field("https://api.openai.com/v1", env="OPENAI_API_BASE")
    mistral_api_base: str = Field("https://api.mistral.ai/v1", env="MISTRAL_API_BASE")
    deepseek_api_base: str = Field("https://api.deepseek.com/v1", env="DEEPSEEK_API_BASE")
    
    # Provider-specific configurations
    mistral: MistralConfig = Field(default_factory=MistralConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


# Create a global config instance
api_config = APIConfig()


def get_api_key(provider: str) -> Optional[str]:
    """Get the API key for the specified provider."""
    if provider == "openai":
        return api_config.openai_api_key
    elif provider == "mistral":
        return api_config.mistral_api_key
    elif provider == "deepseek":
        return api_config.deepseek_api_key
    return None


def get_api_base(provider: str) -> Optional[str]:
    """Get the API base URL for the specified provider."""
    if provider == "openai":
        return api_config.openai_api_base
    elif provider == "mistral":
        return api_config.mistral_api_base
    elif provider == "deepseek":
        return api_config.deepseek_api_base
    return None
