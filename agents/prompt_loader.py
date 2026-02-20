import os
import logging

logger = logging.getLogger(__name__)

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


def load_prompt(filename: str, **kwargs) -> str:
    """Load a prompt file and format it with provided variables."""
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        template = f.read()
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.warning(f"Prompt {filename} missing variable: {e}")
        return template
