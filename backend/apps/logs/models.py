from django.db import models


class RoutingLog(models.Model):
    prompt_summary = models.CharField(max_length=240)
    policy = models.CharField(max_length=64)
    selected_provider = models.CharField(max_length=32)
    selected_model = models.CharField(max_length=120)
    routing_reason = models.TextField()
    latency_ms = models.PositiveIntegerField()
    estimated_tokens = models.PositiveIntegerField()
    response_text = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.policy} -> {self.selected_provider}/{self.selected_model}"
