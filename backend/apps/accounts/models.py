from django.conf import settings
from django.db import models


class ScreenDefinition(models.Model):
    # 권한에서 사용할 화면 목록을 DB에서 관리합니다.
    # screen_id는 프론트 탭 id와 백엔드 required_screen 값에 대응되는 안정적인 키입니다.
    screen_id = models.SlugField(max_length=64, unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "screen_id"]

    def __str__(self):
        return f"{self.label} ({self.screen_id})"


class UserScreenAccess(models.Model):
    # Django 기본 User 모델은 인증 정보만 담당하게 두고, 화면 접근 권한은
    # 별도 1:1 모델에 보관합니다. 이렇게 하면 User 모델 커스터마이징 없이
    # 화면 권한만 독립적으로 확장할 수 있습니다.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="screen_access",
    )
    allowed_screens = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.user.username} screen access"
