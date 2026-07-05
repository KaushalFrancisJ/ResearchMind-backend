import ollama

from app.core.config import settings


def generate_ollama(messages: list[dict], mode: str) -> str:
    """Generate a response using a local Ollama model.

    Args:
        messages: OpenAI-style message list [{"role": ..., "content": ...}]
        mode: "fast" or "thinking"

    Returns:
        The assistant response text.
    """
    model = (
        settings.OLLAMA_THINKING_MODEL if mode == "thinking" else settings.OLLAMA_FAST_MODEL
    )
    client = ollama.Client(host=settings.OLLAMA_URL)
    response = client.chat(model=model, messages=messages)
    return response["message"]["content"], model
