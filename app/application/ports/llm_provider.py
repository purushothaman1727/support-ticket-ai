from abc import ABC, abstractmethod

from app.domain.entities.query_intent import QueryIntent


class LLMProvider(ABC):

    @abstractmethod
    def extract_query_intent(
        self,
        question: str,
    ) -> QueryIntent:
        raise NotImplementedError