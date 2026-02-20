import logging
from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

_client = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        _client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client initialized.")
    return _client


def call_llm(
    prompt: str,
    system: str = "",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    client = get_groq_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.debug(f"LLM call | json_mode={json_mode} | prompt_len={len(prompt)}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.debug(f"LLM response_len={len(content)}")
    return content


def call_llm_with_history(
    messages: list[dict],
    system: str = "",
    temperature: float = 0.5,
    max_tokens: int = 2048,
) -> str:
    client = get_groq_client()
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    logger.debug(f"LLM call with history | turns={len(messages)}")
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content
    return content
