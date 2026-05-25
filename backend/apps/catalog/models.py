from django.db import models


class LLMModel(models.Model):
    PROVIDER_CHOICES = [
        ("ollama", "Ollama"),
        ("openai", "OpenAI"),
        ("gemini", "Gemini"),
        ("openrouter", "OpenRouter"),
    ]
    ROLE_CHOICES = [
        ("general", "General"),
        ("coding", "Coding"),
        ("reasoning", "Reasoning"),
        ("summary", "Summary"),
    ]
    PRIVACY_CHOICES = [
        ("local", "Local"),
        ("external", "External"),
    ]

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    name = models.CharField(max_length=120)
    display_name = models.CharField(max_length=160)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="general")
    quality_level = models.PositiveSmallIntegerField(default=3)
    speed_level = models.PositiveSmallIntegerField(default=3)
    cost_level = models.PositiveSmallIntegerField(default=1)
    privacy_level = models.CharField(max_length=32, choices=PRIVACY_CHOICES, default="local")
    context_window = models.PositiveIntegerField(default=8192)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["provider", "name"]
        unique_together = ("provider", "name")

    def __str__(self):
        return f"{self.provider}/{self.name}"

    def to_candidate(self):
        from apps.catalog.entities import LLMModelCandidate

        # 정책 엔진이 Django 모델에 직접 의존하지 않도록 DB row를 작은 불변 후보 객체로
        # 변환한 뒤 라우팅에 사용합니다.
        return LLMModelCandidate(
            provider=self.provider,
            name=self.name,
            role=self.role,
            quality_level=self.quality_level,
            speed_level=self.speed_level,
            cost_level=self.cost_level,
            privacy_level=self.privacy_level,
            context_window=self.context_window,
        )


class RoutingPolicy(models.Model):
    name = models.SlugField(max_length=64, unique=True)
    display_name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    priority_config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.display_name


class ProviderCredential(models.Model):
    PROVIDER_CHOICES = [
        ("openai", "OpenAI"),
        ("gemini", "Gemini"),
        ("openrouter", "OpenRouter"),
    ]

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=120)
    encrypted_base_url = models.TextField(blank=True)
    encrypted_access_token = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["provider"]

    def __str__(self):
        return self.display_name

    @property
    def base_url(self) -> str:
        return self.get_base_url()

    @base_url.setter
    def base_url(self, value: str):
        self.set_base_url(value)

    @property
    def access_token(self) -> str:
        return self.get_access_token()

    @access_token.setter
    def access_token(self, value: str):
        self.set_access_token(value)

    def set_base_url(self, value: str):
        from apps.catalog.crypto import encrypt_value

        self.encrypted_base_url = encrypt_value(value)

    def get_base_url(self) -> str:
        from apps.catalog.crypto import decrypt_value

        return decrypt_value(self.encrypted_base_url)

    def set_access_token(self, value: str):
        from apps.catalog.crypto import encrypt_value

        self.encrypted_access_token = encrypt_value(value)

    def get_access_token(self) -> str:
        from apps.catalog.crypto import decrypt_value

        return decrypt_value(self.encrypted_access_token)
