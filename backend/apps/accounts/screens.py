DEFAULT_SCREENS = [
    {"id": "dashboard", "label": "Dashboard"},
    {"id": "playground", "label": "Playground"},
    {"id": "simulator", "label": "Routing Simulator"},
    {"id": "models", "label": "Models"},
    {"id": "policies", "label": "Policies"},
    {"id": "routing-rules", "label": "Routing Rules"},
    {"id": "threshold-rules", "label": "Threshold Rules"},
    {"id": "validation-rules", "label": "Validation Rules"},
    {"id": "recovery-strategies", "label": "Recovery Strategies"},
    {"id": "credentials", "label": "Credentials"},
    {"id": "quotas", "label": "Usage Quotas"},
    {"id": "health-rules", "label": "Health Rules"},
    {"id": "health-events", "label": "Health Events"},
    {"id": "health-overrides", "label": "Health Overrides"},
    {"id": "logs", "label": "Routing Logs"},
    {"id": "users", "label": "Users"},
    {"id": "screens", "label": "Screens"},
    {"id": "security-settings", "label": "Security Settings"},
    {"id": "sessions", "label": "User Sessions"},
    {"id": "audit-logs", "label": "Audit Logs"},
]

ALL_SCREENS = [screen["id"] for screen in DEFAULT_SCREENS]


def get_available_screens(include_inactive: bool = False) -> list[dict[str, object]]:
    # 마이그레이션 전 테스트나 초기 상태에서도 기본 화면 목록은 반환되도록 fallback을 둡니다.
    from apps.accounts.models import ScreenDefinition

    queryset = ScreenDefinition.objects.all()
    if not include_inactive:
        queryset = queryset.filter(is_active=True)
    screens = [
        {
            "pk": screen.pk,
            "id": screen.screen_id,
            "label": screen.label,
            "description": screen.description,
            "sort_order": screen.sort_order,
            "is_active": screen.is_active,
        }
        for screen in queryset
    ]
    return screens or DEFAULT_SCREENS


def get_available_screen_ids(include_inactive: bool = False) -> list[str]:
    return [screen["id"] for screen in get_available_screens(include_inactive=include_inactive)]


def normalize_allowed_screens(value: list[str]) -> list[str]:
    # 관리자가 직접 입력한 화면 id도 허용하되, 빈 값과 중복 값은 저장 전에 제거합니다.
    normalized = []
    for screen in value:
        if not isinstance(screen, str):
            continue
        screen_id = screen.strip()
        if screen_id and screen_id not in normalized:
            normalized.append(screen_id)
    return normalized
