"""Custom RAG evaluation using the configured LLM (Groq in production, Ollama in development).

Evaluates faithfulness and relevancy using an LLM-as-judge pattern,
storing results in the ChatEvaluation table.
"""

from app.services.llm.llm_factory import generate

_FAITHFULNESS_PROMPT = """\
You are an evaluation assistant. Given a context and an answer, score how \
faithful the answer is to the context (i.e., does it stay grounded without \
hallucinating).

Context:
{context}

Answer:
{answer}

Respond with EXACTLY two lines:
Score: <number between 0.0 and 1.0>
Reason: <one sentence explanation>"""

_RELEVANCY_PROMPT = """\
You are an evaluation assistant. Given a question and an answer, score how \
relevant the answer is to the question.

Question:
{query}

Answer:
{answer}

Respond with EXACTLY two lines:
Score: <number between 0.0 and 1.0>
Reason: <one sentence explanation>"""


def _parse_score_and_reason(text: str) -> tuple[float, str]:
    """Extract score and reason from the LLM response."""
    score = 0.5
    reason = ""
    for line in text.strip().splitlines():
        line = line.strip()
        if line.lower().startswith("score:"):
            try:
                score = float(line.split(":", 1)[1].strip())
                score = max(0.0, min(1.0, score))  # clamp to [0, 1]
            except ValueError:
                pass
        elif line.lower().startswith("reason:"):
            reason = line.split(":", 1)[1].strip()
    return score, reason


def evaluate(
    query: str,
    answer: str,
    context: str,
    mode: str = "fast",
) -> dict[str, float | str]:
    """Evaluate a RAG response for faithfulness and relevancy.

    Uses the same LLM backend as the chat endpoint (Groq in production,
    Ollama in development), so no extra dependencies are needed.

    Args:
        query: The user's original question
        answer: The generated answer to evaluate
        context: The retrieved context that was used for generation
        mode: LLM mode — "fast" or "thinking"

    Returns:
        Dictionary with faithfulness_score, faithfulness_reason,
        relevancy_score, relevancy_reason.
    """
    # Faithfulness: is the answer grounded in the context?
    faithfulness_text, _ = generate(
        messages=[
            {
                "role": "user",
                "content": _FAITHFULNESS_PROMPT.format(context=context, answer=answer),
            }
        ],
        mode=mode,
    )
    faithfulness_score, faithfulness_reason = _parse_score_and_reason(faithfulness_text)

    # Relevancy: does the answer address the question?
    relevancy_text, _ = generate(
        messages=[
            {
                "role": "user",
                "content": _RELEVANCY_PROMPT.format(query=query, answer=answer),
            }
        ],
        mode=mode,
    )
    relevancy_score, relevancy_reason = _parse_score_and_reason(relevancy_text)

    return {
        "faithfulness_score": faithfulness_score,
        "faithfulness_reason": faithfulness_reason,
        "relevancy_score": relevancy_score,
        "relevancy_reason": relevancy_reason,
    }
