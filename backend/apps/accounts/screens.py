DEFAULT_SCREENS = [
    {"id": "dashboard", "label": "Dashboard"},
    {"id": "playground", "label": "Playground"},
    {"id": "models", "label": "Models"},
    {"id": "policies", "label": "Policies"},
    {"id": "credentials", "label": "Credentials"},
    {"id": "logs", "label": "Routing Logs"},
    {"id": "users", "label": "Users"},
    {"id": "screens", "label": "Screens"},
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
