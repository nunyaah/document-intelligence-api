from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a precise document analysis assistant. Your task is to answer questions based ONLY on the provided document context.

Rules:
1. Answer using ONLY information from the context below. Do not use prior knowledge.
2. If the answer is not in the context, say "I cannot find this information in the provided document."
3. When you use information from a source, cite it inline as [SOURCE N] matching the source labels in the context.
4. Be concise but complete. Prefer bullet points for multi-part answers.
5. Never fabricate facts, numbers, names, or dates.
"""

HUMAN_PROMPT_TEMPLATE = """Context from document "{filename}":

{context}

---

Question: {question}

Answer (cite sources as [SOURCE N]):"""


def _build_context_string(chunks) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        page = chunk.payload.get("page_number", "?")
        text = chunk.payload.get("text", "")
        parts.append(f"[SOURCE {i}] (Page {page})\n{text}")
    return "\n\n".join(parts)


def _get_groq_client():
    from groq import Groq

    settings = get_settings()
    return Groq(api_key=settings.groq_api_key)


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
def _call_groq(client, messages: list[dict], model: str, max_tokens: int, temperature: float) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


async def generate_answer(
    question: str,
    chunks: list,
    filename: str,
    conversation_history: list | None = None,
) -> tuple[str, str]:
    """Call the LLM and return (answer_text, model_name)."""
    from app.utils.exceptions import LLMUnavailableError

    settings = get_settings()

    if not settings.groq_api_key:
        raise LLMUnavailableError("GROQ_API_KEY is not configured.")

    context = _build_context_string(chunks)
    human_prompt = HUMAN_PROMPT_TEMPLATE.format(filename=filename, context=context, question=question)

    # Inject prior turns between system prompt and the current user message
    # so the LLM can resolve references like "this strategy" or "it".
    history_messages = []
    for turn in conversation_history or []:
        role = turn.get("role")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            history_messages.append({"role": role, "content": content})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history_messages,
        {"role": "user", "content": human_prompt},
    ]

    try:
        client = _get_groq_client()
        answer = _call_groq(
            client,
            messages=messages,
            model=settings.groq_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
        )
        return answer, settings.groq_model
    except Exception as exc:
        logger.error("LLM call failed", extra={"error": str(exc)})
        raise LLMUnavailableError(str(exc)) from exc
