from app.infrastructure.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)
from app.infrastructure.llm.ollama_client import OllamaClient


def main():
    client = OllamaClient(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        timeout=OLLAMA_TIMEOUT,
    )

    questions = [
        "How many open tickets are there?",
        "What is the average customer rating for Technical tickets?",
        "Which agent resolved the most tickets?",
        "Which agent has the lowest average rating?",
        "Which agent resolved the most tickets this month?",
        "How many critical tickets were not resolved within 12 hours?",
        "Are there any anomalies in resolution times this week?",
    ]

    for question in questions:
        print("\n" + "=" * 60)
        print(f"Question: {question}")

        try:
            intent = client.extract_query_intent(question)

            print("Validated intent:")
            print(intent)

        except Exception as exc:
            print(f"Error: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
