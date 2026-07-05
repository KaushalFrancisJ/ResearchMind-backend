from app.core.config import settings
from app.services.llm.groq_provider import generate_groq
from app.services.llm.ollama_provider import generate_ollama


def generate(messages: list[dict], mode: str = "fast") -> tuple[str, str]:
    """Route to the correct LLM backend based on the ENV setting.

    In development  → Ollama (local)
    In production   → Groq API

    Args:
        messages: OpenAI-style message list [{"role": ..., "content": ...}]
        mode: "fast" or "thinking"

    Returns:
        Tuple of (response text, model name used).
    """
    if settings.ENV == "production":
        return generate_groq(messages, mode)
    return generate_ollama(messages, mode)
