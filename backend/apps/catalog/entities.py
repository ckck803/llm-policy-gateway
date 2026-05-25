from dataclasses import dataclass


@dataclass(frozen=True)
class LLMModelCandidate:
    provider: str
    name: str
    role: str
    quality_level: int
    speed_level: int
    cost_level: int
    privacy_level: str
    context_window: int
