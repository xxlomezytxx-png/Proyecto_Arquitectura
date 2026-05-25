import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.chat_use_case import ChatUseCase
from app.infrastructure.clients.catalog_client import CatalogClient
from app.infrastructure.clients.inventory_client import InventoryClient
from app.infrastructure.clients.pricing_client import PricingClient
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.interaction_repository import (
    SqlInteractionRepository,
)

router = APIRouter(tags=["assistant"])


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    intent: str
    answer: str
    interaction_id: str | None


def _process_chat(body: ChatRequest, db: Session) -> ChatResponse:
    if not body.question or not body.question.strip():
        raise HTTPException(status_code=422, detail="La pregunta no puede estar vacía")

    session_id = body.session_id or str(uuid.uuid4())

    repo = SqlInteractionRepository(db)

    use_case = ChatUseCase(
        repo=repo,
        catalog=CatalogClient(),
        pricing=PricingClient(),
        inventory=InventoryClient(),
    )

    interaction = use_case.execute(
        session_id=session_id,
        question=body.question.strip(),
    )

    return ChatResponse(
        session_id=interaction.session_id,
        intent=interaction.interpreted_intent,
        answer=interaction.answer_text,
        interaction_id=interaction.id,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return _process_chat(body, db)


@router.post("/assistant/ask", response_model=ChatResponse)
def assistant_ask(body: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return _process_chat(body, db)


@router.get("/assistant/history")
def assistant_history(
    session_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    repo = SqlInteractionRepository(db)
    records = repo.find_by_session(session_id)

    return {
        "session_id": session_id,
        "total": len(records),
        "items": [
            {
                "id": item.id,
                "question": item.user_question,
                "intent": item.interpreted_intent,
                "answer": item.answer_text,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in records
        ],
    }