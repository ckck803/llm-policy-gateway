from django.core.management.base import BaseCommand

from apps.catalog.models import LLMModel, RoutingPolicy


class Command(BaseCommand):
    help = "Seed demo Ollama models and routing policies."

    def handle(self, *args, **options):
        models = [
            {
                "provider": "ollama",
                "name": "llama3.1:8b",
                "display_name": "Llama 3.1 8B",
                "role": "general",
                "quality_level": 3,
                "speed_level": 5,
                "cost_level": 1,
                "privacy_level": "local",
                "context_window": 8192,
                "input_token_price_per_1m": 0,
                "output_token_price_per_1m": 0,
                "average_latency_ms": 2500,
                "timeout_seconds": 120,
                "is_active": True,
            },
            {
                "provider": "ollama",
                "name": "codellama:latest",
                "display_name": "Code Llama",
                "role": "coding",
                "quality_level": 4,
                "speed_level": 3,
                "cost_level": 1,
                "privacy_level": "local",
                "context_window": 16384,
                "input_token_price_per_1m": 0,
                "output_token_price_per_1m": 0,
                "average_latency_ms": 4000,
                "timeout_seconds": 120,
                "is_active": True,
            },
            {
                "provider": "ollama",
                "name": "qwen3:8b",
                "display_name": "Qwen 3 8B",
                "role": "reasoning",
                "quality_level": 4,
                "speed_level": 4,
                "cost_level": 1,
                "privacy_level": "local",
                "context_window": 32768,
                "input_token_price_per_1m": 0,
                "output_token_price_per_1m": 0,
                "average_latency_ms": 5500,
                "timeout_seconds": 180,
                "is_active": True,
            },
            {
                "provider": "openai",
                "name": "gpt-4.1-mini",
                "display_name": "GPT-4.1 Mini",
                "role": "general",
                "quality_level": 4,
                "speed_level": 4,
                "cost_level": 3,
                "privacy_level": "external",
                "context_window": 128000,
                "input_token_price_per_1m": 0.4,
                "output_token_price_per_1m": 1.6,
                "average_latency_ms": 1800,
                "timeout_seconds": 120,
                "is_active": False,
            },
            {
                "provider": "gemini",
                "name": "gemini-2.5-flash",
                "display_name": "Gemini 2.5 Flash",
                "role": "general",
                "quality_level": 4,
                "speed_level": 5,
                "cost_level": 2,
                "privacy_level": "external",
                "context_window": 1000000,
                "input_token_price_per_1m": 0.3,
                "output_token_price_per_1m": 2.5,
                "average_latency_ms": 1600,
                "timeout_seconds": 120,
                "is_active": False,
            },
            {
                "provider": "openrouter",
                "name": "openai/gpt-4.1-mini",
                "display_name": "OpenRouter GPT-4.1 Mini",
                "role": "general",
                "quality_level": 4,
                "speed_level": 4,
                "cost_level": 3,
                "privacy_level": "external",
                "context_window": 128000,
                "input_token_price_per_1m": 0.4,
                "output_token_price_per_1m": 1.6,
                "average_latency_ms": 2200,
                "timeout_seconds": 120,
                "is_active": False,
            },
        ]
        for payload in models:
            LLMModel.objects.update_or_create(
                provider=payload["provider"],
                name=payload["name"],
                defaults=payload,
            )

        policies = [
            ("cost-first", "Cost First", "Prefer low-cost and fast local models."),
            ("quality-first", "Quality First",
             "Prefer stronger models for reasoning-heavy prompts."),
            ("privacy-first", "Privacy First",
             "Keep sensitive prompts on local models."),
        ]
        for name, display_name, description in policies:
            RoutingPolicy.objects.update_or_create(
                name=name,
                defaults={
                    "display_name": display_name,
                    "description": description,
                    "priority_config": {},
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            "Seeded demo models and policies."))
