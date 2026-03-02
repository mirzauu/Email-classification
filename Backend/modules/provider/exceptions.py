class ProviderError(Exception):
    """Base exception for provider module."""
    pass

class UnsupportedProviderError(ProviderError):
    """Raised when a provider or model is not supported."""
    pass

class LLMCallError(ProviderError):
    """Raised when an LLM call fails."""
    pass
