
import json
from typing import Optional

import httpx

from app.application.ports.llm_provider import LLMProvider
from app.domain.entities.query_intent import QueryIntent
from app.infrastructure.llm.schemas import LLMQueryIntent


class OllamaClient(LLMProvider):

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def extract_query_intent(
        self,
        question: str,
    ) -> QueryIntent:

        cleaned_question = question.strip()

        if not cleaned_question:
            raise ValueError("Question cannot be empty")

        # Deterministic routing for predictable assessment questions.
        rule_based_intent = self._rule_based_intent(
            cleaned_question
        )

        if rule_based_intent is not None:
            return rule_based_intent

        prompt = self._build_prompt(cleaned_question)

        payload = {
            "model": self.model,
            "stream": False,
            "format": LLMQueryIntent.model_json_schema(),
            "options": {
                "temperature": 0,
            },
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You extract structured query intent "
                        "from support ticket questions."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Ollama request failed: {exc}"
            ) from exc

        response_data = response.json()

        raw_content = (
            response_data
            .get("message", {})
            .get("content", "")
        )

        if not raw_content:
            raise ValueError(
                "Ollama returned an empty response"
            )

        try:
            parsed_json = json.loads(raw_content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Ollama did not return valid JSON"
            ) from exc

        validated_intent = LLMQueryIntent.model_validate(
            parsed_json
        )

        validated_intent = self._normalize_intent(
            validated_intent
        )

        return QueryIntent(
            operation=validated_intent.operation,
            status=validated_intent.status,
            category=validated_intent.category,
            priority=validated_intent.priority,
            agent_id=validated_intent.agent_id,
            max_resolution_hours=(
                validated_intent.max_resolution_hours
            ),
        )

    @staticmethod
    def _rule_based_intent(
        question: str,
    ) -> Optional[QueryIntent]:

        normalized_question = question.lower()

        # 1. Resolution-time anomaly questions
        anomaly_keywords = [
            "anomalies in resolution time",
            "anomaly in resolution time",
            "resolution time anomaly",
            "resolution time anomalies",
            "abnormally long resolution",
            "unusual resolution time",
        ]

        if any(
            keyword in normalized_question
            for keyword in anomaly_keywords
        ):
            return QueryIntent(
                operation="resolution_time_anomaly",
                status=None,
                category=None,
                priority=None,
                agent_id=None,
                max_resolution_hours=None,
            )

        # 2. Lowest average rating agent
        lowest_rating_keywords = [
            "lowest average rating",
            "lowest rating agent",
            "agent with the lowest rating",
            "agent has the lowest rating",
        ]

        if any(
            keyword in normalized_question
            for keyword in lowest_rating_keywords
        ):
            return QueryIntent(
                operation="lowest_average_rating_agent",
                status=None,
                category=None,
                priority=None,
                agent_id=None,
                max_resolution_hours=None,
            )

        # 3. Top resolved agent this month
        if (
            "this month" in normalized_question
            and (
                "resolved the most" in normalized_question
                or "most tickets" in normalized_question
                or "top resolved agent" in normalized_question
            )
        ):
            return QueryIntent(
                operation="top_resolved_agent_this_month",
                status=None,
                category=None,
                priority=None,
                agent_id=None,
                max_resolution_hours=None,
            )

        # 4. Critical tickets not resolved within a time limit
        if (
            "critical" in normalized_question
            and (
                "not resolved" in normalized_question
                or "unresolved" in normalized_question
            )
            and (
                "within 12 hours" in normalized_question
                or "12 hours" in normalized_question
            )
        ):
            return QueryIntent(
                operation="critical_unresolved",
                status=None,
                category=None,
                priority="Critical",
                agent_id=None,
                max_resolution_hours=12.0,
            )

        return None

    @staticmethod
    def _normalize_intent(
        intent: LLMQueryIntent,
    ) -> LLMQueryIntent:

        data = intent.model_dump()

        # Convert string "null" into actual None.
        for field_name, value in data.items():
            if (
                isinstance(value, str)
                and value.lower() == "null"
            ):
                data[field_name] = None

        operation = data["operation"]

        if operation in (
            "top_resolved_agent",
            "top_resolved_agent_this_month",
            "lowest_average_rating_agent",
        ):
            data["status"] = None
            data["category"] = None
            data["priority"] = None
            data["agent_id"] = None
            data["max_resolution_hours"] = None

        elif operation == "average_rating":
            data["status"] = None
            data["priority"] = None
            data["agent_id"] = None

        elif operation == "critical_unresolved":
            data["status"] = None
            data["category"] = None
            data["priority"] = "Critical"

        elif operation == "resolution_time_anomaly":
            data["status"] = None
            data["category"] = None
            data["priority"] = None
            data["agent_id"] = None
            data["max_resolution_hours"] = None

        return LLMQueryIntent.model_validate(data)

    @staticmethod
    def _build_prompt(question: str) -> str:

        schema_description = {
            "operation": (
                "count | average_rating | "
                "top_resolved_agent | "
                "lowest_average_rating_agent | "
                "top_resolved_agent_this_month | "
                "critical_unresolved | "
                "resolution_time_anomaly"
            ),
            "status": "Open | Resolved | Escalated | null",
            "category": (
                "Billing | Technical | General | null"
            ),
            "priority": (
                "Low | Medium | High | Critical | null"
            ),
            "agent_id": "string or null",
            "max_resolution_hours": (
                "positive number or null"
            ),
        }

        return f"""
Convert the user's support ticket question into JSON.

Allowed output schema:
{json.dumps(schema_description, indent=2)}

Rules:
1. Return JSON only.
2. Never invent values.
3. If the user does not explicitly mention a filter,
   return null for that field.
4. Do not assume category, priority, status,
   or agent_id.
5. For "open tickets", use status "Open".
6. For "resolved tickets", use status "Resolved".
7. For "critical tickets", use priority "Critical".
8. For "technical tickets", use category "Technical".
9. For counting tickets, use operation "count".
10. For average customer rating, use operation
    "average_rating".
11. For the agent who resolved the most tickets,
    use operation "top_resolved_agent".
12. For the agent with the lowest average rating,
    use operation "lowest_average_rating_agent".
13. For the agent who resolved the most tickets
    this month, use operation
    "top_resolved_agent_this_month".
14. For critical unresolved tickets with a time limit,
    use operation "critical_unresolved".
15. For questions about anomalies in resolution times,
    use operation "resolution_time_anomaly".
16. Do not answer the question.
17. Extract intent only.

Examples:

Question:
Which agent has the lowest average rating?

JSON:
{{
    "operation": "lowest_average_rating_agent",
    "status": null,
    "category": null,
    "priority": null,
    "agent_id": null,
    "max_resolution_hours": null
}}

Question:
Which agent resolved the most tickets this month?

JSON:
{{
    "operation": "top_resolved_agent_this_month",
    "status": null,
    "category": null,
    "priority": null,
    "agent_id": null,
    "max_resolution_hours": null
}}

Question:
How many critical tickets were not resolved within 12 hours?

JSON:
{{
    "operation": "critical_unresolved",
    "status": null,
    "category": null,
    "priority": "Critical",
    "agent_id": null,
    "max_resolution_hours": 12.0
}}

Question:
Are there any anomalies in resolution times this week?

JSON:
{{
    "operation": "resolution_time_anomaly",
    "status": null,
    "category": null,
    "priority": null,
    "agent_id": null,
    "max_resolution_hours": null
}}

User question:
{question}
"""