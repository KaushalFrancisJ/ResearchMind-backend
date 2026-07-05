from groq import Groq

from app.core.config import settings


def generate_groq(messages: list[dict], mode: str) -> tuple[str, str]:
    """Generate a response using the Groq API.

    Args:
        messages: OpenAI-style message list [{"role": ..., "content": ...}]
        mode: "fast" or "thinking"

    Returns:
        Tuple of (response text, model name used).
    """
    model = (
        settings.GROQ_THINKING_MODEL if mode == "thinking" else settings.GROQ_FAST_MODEL
    )
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content.strip(), model
