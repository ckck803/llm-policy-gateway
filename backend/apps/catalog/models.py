from django.db import models
from django.conf import settings


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
    TIER_CHOICES = [
        ("lightweight", "Lightweight"),
        ("standard", "Standard"),
        ("advanced", "Advanced"),
        ("long_context", "Long Context"),
        ("structured", "Structured"),
    ]
    PRIVACY_CHOICES = [
        ("local", "Local"),
        ("external", "External"),
    ]

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    name = models.CharField(max_length=120)
    display_name = models.CharField(max_length=160)
    model_tier = models.CharField(max_length=32, choices=TIER_CHOICES, default="standard")
    provider_credential = models.ForeignKey(
        "ProviderCredential",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="models",
    )
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="general")
    quality_level = models.PositiveSmallIntegerField(default=3)
    speed_level = models.PositiveSmallIntegerField(default=3)
    cost_level = models.PositiveSmallIntegerField(default=1)
    privacy_level = models.CharField(max_length=32, choices=PRIVACY_CHOICES, default="local")
    context_window = models.PositiveIntegerField(default=8192)
    input_token_price_per_1m = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    output_token_price_per_1m = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    average_latency_ms = models.PositiveIntegerField(default=0)
    timeout_seconds = models.PositiveIntegerField(default=120)
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
            model_tier=self.model_tier,
            role=self.role,
            quality_level=self.quality_level,
            speed_level=self.speed_level,
            cost_level=self.cost_level,
            privacy_level=self.privacy_level,
            context_window=self.context_window,
            input_token_price_per_1m=self.input_token_price_per_1m,
            output_token_price_per_1m=self.output_token_price_per_1m,
            average_latency_ms=self.average_latency_ms,
            timeout_seconds=self.timeout_seconds,
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


class RoutingRule(models.Model):
    CONDITION_CHOICES = [
        ("general", "General/simple query"),
        ("code", "Code or technical request"),
        ("reasoning", "Reasoning request"),
        ("long_context", "Long context request"),
        ("structured_output", "SQL/JSON structured output"),
        ("sensitive", "Sensitive data request"),
        ("always", "Always"),
    ]
    TARGET_TIER_CHOICES = LLMModel.TIER_CHOICES

    rule_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    condition_key = models.CharField(max_length=32, choices=CONDITION_CHOICES, default="general")
    target_tier = models.CharField(max_length=32, choices=TARGET_TIER_CHOICES)
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "rule_id"]

    def __str__(self):
        return f"{self.rule_id} - {self.name}"


class ThresholdRule(models.Model):
    METRIC_CHOICES = [
        ("estimated_tokens", "Estimated tokens"),
        ("p95_latency_ms", "p95 latency ms"),
        ("timeout_seconds", "Timeout seconds"),
        ("parse_fail_rate", "Parse fail rate"),
        ("failure_rate", "Failure rate"),
    ]
    OPERATOR_CHOICES = [
        ("gte", ">="),
        ("lte", "<="),
    ]
    ACTION_CHOICES = [
        ("prefer_tier", "Prefer model tier"),
        ("set_max_tokens", "Set max tokens"),
    ]
    TARGET_TIER_CHOICES = LLMModel.TIER_CHOICES

    rule_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    metric_key = models.CharField(max_length=32, choices=METRIC_CHOICES, default="estimated_tokens")
    operator = models.CharField(max_length=8, choices=OPERATOR_CHOICES, default="gte")
    threshold_value = models.DecimalField(max_digits=12, decimal_places=4)
    action_on_trigger = models.CharField(max_length=32, choices=ACTION_CHOICES, default="prefer_tier")
    target_tier = models.CharField(max_length=32, choices=TARGET_TIER_CHOICES, blank=True, default="")
    max_tokens = models.PositiveIntegerField(null=True, blank=True)
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "rule_id"]

    def __str__(self):
        return f"{self.rule_id} - {self.name}"


class ResponseValidationRule(models.Model):
    CONDITION_CHOICES = RoutingRule.CONDITION_CHOICES
    VALIDATION_CHOICES = [
        ("non_empty", "Non-empty response"),
        ("json", "JSON parse validation"),
        ("sql", "SQL format validation"),
    ]
    ACTION_CHOICES = [
        ("strict_retry", "Strict retry"),
        ("fallback", "Fallback"),
        ("escalate", "Escalate to tier"),
        ("block", "Block response"),
    ]
    TARGET_TIER_CHOICES = LLMModel.TIER_CHOICES

    rule_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    recovery_strategy = models.ForeignKey(
        "RecoveryStrategy",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="validation_rules",
    )
    condition_key = models.CharField(max_length=32, choices=CONDITION_CHOICES, default="structured_output")
    validation_type = models.CharField(max_length=32, choices=VALIDATION_CHOICES, default="json")
    action_on_fail = models.CharField(max_length=32, choices=ACTION_CHOICES, default="strict_retry")
    retry_prompt = models.TextField(blank=True)
    max_retries = models.PositiveIntegerField(default=1)
    target_tier = models.CharField(max_length=32, choices=TARGET_TIER_CHOICES, blank=True, default="")
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "rule_id"]

    def __str__(self):
        return f"{self.rule_id} - {self.name}"


class RecoveryStrategy(models.Model):
    TRIGGER_CHOICES = [
        ("validation_fail", "Validation failure"),
        ("timeout", "Timeout"),
        ("api_fail", "API failure"),
        ("parse_fail", "Parse failure"),
        ("low_confidence", "Low confidence"),
    ]
    ACTION_CHOICES = ResponseValidationRule.ACTION_CHOICES
    TARGET_TIER_CHOICES = LLMModel.TIER_CHOICES

    strategy_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    trigger_event = models.CharField(max_length=32, choices=TRIGGER_CHOICES, default="validation_fail")
    action = models.CharField(max_length=32, choices=ACTION_CHOICES, default="strict_retry")
    retry_prompt = models.TextField(blank=True)
    max_retries = models.PositiveIntegerField(default=1)
    target_tier = models.CharField(max_length=32, choices=TARGET_TIER_CHOICES, blank=True, default="")
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "strategy_id"]

    def __str__(self):
        return f"{self.strategy_id} - {self.name}"


class ProviderCredential(models.Model):
    PROVIDER_CHOICES = [
        ("openai", "OpenAI"),
        ("gemini", "Gemini"),
        ("openrouter", "OpenRouter"),
    ]

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    display_name = models.CharField(max_length=120)
    encrypted_base_url = models.TextField(blank=True)
    encrypted_access_token = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    token_rotated_at = models.DateTimeField(null=True, blank=True)
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

    def mark_used(self):
        from django.utils import timezone

        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])


class UsageQuota(models.Model):
    ACTION_CHOICES = [
        ("block", "Block request"),
        ("local_fallback", "Fallback to local"),
    ]
    PROVIDER_CHOICES = [
        ("", "All providers"),
        ("ollama", "Ollama"),
        ("openai", "OpenAI"),
        ("gemini", "Gemini"),
        ("openrouter", "OpenRouter"),
    ]

    name = models.CharField(max_length=120)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="usage_quotas",
    )
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES, blank=True, default="")
    monthly_request_limit = models.PositiveIntegerField(null=True, blank=True)
    monthly_cost_limit_usd = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    action_on_exceed = models.CharField(max_length=32, choices=ACTION_CHOICES, default="local_fallback")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ModelHealthRule(models.Model):
    PROVIDER_CHOICES = [
        ("", "All providers"),
        ("ollama", "Ollama"),
        ("openai", "OpenAI"),
        ("gemini", "Gemini"),
        ("openrouter", "OpenRouter"),
    ]
    ACTION_CHOICES = [
        ("exclude", "Exclude from routing"),
    ]

    name = models.CharField(max_length=120)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES, blank=True, default="")
    model_name = models.CharField(max_length=120, blank=True, default="")
    window_minutes = models.PositiveIntegerField(default=60)
    min_requests = models.PositiveIntegerField(default=5)
    max_failure_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_average_latency_ms = models.PositiveIntegerField(null=True, blank=True)
    action_on_trigger = models.CharField(max_length=32, choices=ACTION_CHOICES, default="exclude")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ModelHealthEvent(models.Model):
    EVENT_CHOICES = [
        ("triggered", "Triggered"),
        ("recovered", "Recovered"),
    ]
    STATUS_CHOICES = [
        ("healthy", "Healthy"),
        ("unhealthy", "Unhealthy"),
    ]

    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    provider = models.CharField(max_length=32)
    model_name = models.CharField(max_length=120)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    rule = models.ForeignKey(
        ModelHealthRule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    rule_name = models.CharField(max_length=120, blank=True, default="")
    reason = models.TextField(blank=True)
    request_count = models.PositiveIntegerField(default=0)
    failures = models.PositiveIntegerField(default=0)
    failure_rate = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    average_latency_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider}/{self.model_name} {self.event_type}"


class ModelHealthOverride(models.Model):
    OVERRIDE_CHOICES = [
        ("force_healthy", "Force healthy"),
        ("force_unhealthy", "Force unhealthy"),
    ]
    PROVIDER_CHOICES = [
        ("", "All providers"),
        ("ollama", "Ollama"),
        ("openai", "OpenAI"),
        ("gemini", "Gemini"),
        ("openrouter", "OpenRouter"),
    ]

    name = models.CharField(max_length=120)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES, blank=True, default="")
    model_name = models.CharField(max_length=120, blank=True, default="")
    override_type = models.CharField(max_length=32, choices=OVERRIDE_CHOICES)
    reason = models.TextField(blank=True, default="")
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="model_health_overrides",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        scope = f"{self.provider or '*'}/{self.model_name or '*'}"
        return f"{scope} {self.override_type}"
