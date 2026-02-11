from langchain_groq import ChatGroq

from app.settings import settings
from app_log.logger import get_logger

logger = get_logger("llm_factory")


def get_llm():
    """
    Returns a configured LLM instance.

    This is the ONLY place in the codebase
    that knows which LLM provider is used.
    """
    logger.info(
        "Initializing LLM",
        extra={
            "provider": "groq",
            "model": settings.groq_model,
            "temperature": settings.groq_temperature,
        },
    )

    llm = ChatGroq(
        groq_api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=settings.groq_temperature,
        max_tokens=settings.groq_max_tokens,
    )

    return llm
