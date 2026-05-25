import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.entities.interaction import AssistantInteraction
from app.domain.interfaces.interaction_repository import InteractionRepository
from app.infrastructure.database.models import AssistantInteractionModel


class SqlInteractionRepository(InteractionRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, interaction: AssistantInteraction) -> AssistantInteraction:
        record_id = str(uuid.uuid4())
        model = AssistantInteractionModel(
            id=record_id,
            session_id=interaction.session_id,
            user_question=interaction.user_question,
            interpreted_intent=interaction.interpreted_intent,
            answer_text=interaction.answer_text,
            created_at=interaction.created_at or datetime.now(timezone.utc),
        )
        self._db.add(model)
        try:
            self._db.commit()
            self._db.refresh(model)
        except Exception:
            self._db.rollback()
            raise
        return AssistantInteraction(
            id=model.id,
            session_id=model.session_id,
            user_question=model.user_question,
            interpreted_intent=model.interpreted_intent,
            answer_text=model.answer_text,
            created_at=model.created_at,
        )

    def find_by_session(self, session_id: str) -> list[AssistantInteraction]:
        records = (
            self._db.query(AssistantInteractionModel)
            .filter(AssistantInteractionModel.session_id == session_id)
            .order_by(AssistantInteractionModel.created_at)
            .all()
        )
        return [
            AssistantInteraction(
                id=r.id,
                session_id=r.session_id,
                user_question=r.user_question,
                interpreted_intent=r.interpreted_intent,
                answer_text=r.answer_text,
                created_at=r.created_at,
            )
            for r in records
        ]
