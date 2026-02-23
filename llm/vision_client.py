"""
Groq Vision Client — isolated from the primary groq_client.py.

Uses GROQ_VISION_API_KEY + GROQ_VISION_MODEL (a separate Groq account
and a vision-capable model).  Never touches the primary GROQ_API_KEY.
"""

import base64
import logging

from groq import Groq
from config.settings import GROQ_VISION_API_KEY, GROQ_VISION_MODEL

logger = logging.getLogger(__name__)

# ── Singleton ────────────────────────────────────────────────────────────────
_vision_client = None


def _get_vision_client() -> Groq:
    """Return (or create) the dedicated vision Groq client."""
    global _vision_client
    if _vision_client is None:
        if not GROQ_VISION_API_KEY:
            raise ValueError(
                "GROQ_VISION_API_KEY is not set. "
                "Please add it to your .env file to enable image analysis."
            )
        _vision_client = Groq(api_key=GROQ_VISION_API_KEY)
        logger.info("VISION | vision_client initialized (model=%s)", GROQ_VISION_MODEL)
    return _vision_client


# ── Public API ───────────────────────────────────────────────────────────────
def analyze_image(
    image_bytes: bytes,
    media_type: str,
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> str:
    """Send an image + text prompt to the Groq vision model and return the
    model's text response.

    Parameters
    ----------
    image_bytes : raw bytes of the image file
    media_type  : MIME type, e.g. "image/jpeg", "image/png", "image/webp"
    prompt      : text instruction to accompany the image
    max_tokens  : maximum response length
    temperature : sampling temperature
    """
    logger.info("VISION | analyze_image | model=%s media=%s", GROQ_VISION_MODEL, media_type)

    try:
        client = _get_vision_client()

        base64_str = base64.b64encode(image_bytes).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{base64_str}",
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        response = client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        content = response.choices[0].message.content
        logger.info("VISION | analyze_image | response_len=%d", len(content))
        return content

    except ValueError:
        # Re-raise config errors as-is so callers can show a clear message
        raise
    except Exception as e:
        logger.error("VISION | analyze_image | ERROR: %s", e)
        raise RuntimeError(f"Vision analysis failed: {e}") from e
