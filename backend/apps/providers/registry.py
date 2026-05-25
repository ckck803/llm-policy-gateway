from apps.providers.gemini import GeminiProvider
from apps.providers.ollama import OllamaProvider
from apps.providers.openai import OpenAIProvider
from apps.providers.openrouter import OpenRouterProvider


class ProviderRegistry:
    def __init__(self):
        self._provider_factories = {
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "openrouter": OpenRouterProvider,
        }
        self._providers = {}

    def get(self, provider_name: str):
        if provider_name not in self._provider_factories:
            raise ValueError(f"Provider '{provider_name}' is not configured yet.")
        if provider_name not in self._providers:
            self._providers[provider_name] = self._provider_factories[provider_name]()
        return self._providers[provider_name]
