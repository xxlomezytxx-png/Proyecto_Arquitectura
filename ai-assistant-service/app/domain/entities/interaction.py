from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class AssistantInteraction:
    session_id: str
    user_question: str
    interpreted_intent: str
    answer_text: str
    id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
