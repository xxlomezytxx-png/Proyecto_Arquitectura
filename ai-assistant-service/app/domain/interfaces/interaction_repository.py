from abc import ABC, abstractmethod

from app.domain.entities.interaction import AssistantInteraction


class InteractionRepository(ABC):
    @abstractmethod
    def save(self, interaction: AssistantInteraction) -> AssistantInteraction: ...

    @abstractmethod
    def find_by_session(self, session_id: str) -> list[AssistantInteraction]: ...
