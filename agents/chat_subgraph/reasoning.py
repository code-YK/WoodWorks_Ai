import traceback
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


def reasoning_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | Reasoning | ENTER")

    context = state.get("retrieved_context", "")
    history = state.get("conversation_history") or []

    user_content = (
        state.get("user_message")
        or state.get("refined_query")
        or ""
    ).strip()

    if not user_content:
        logger.warning("NODE | Reasoning | No user content found — using fallback")
        return {
            **state,
            "reasoning_output": "Could you clarify what you'd like to know?",
            "current_node": "reasoning",
        }

    system_prompt = load_prompt(
        "chat.txt",
        product_catalog_summary=context,
        conversation_history=""
    )

    # ── Image context injection (vision feature) ────────────────────────
    image_hint = state.get("image_spec_hint")
    if image_hint:
        image_context = (
            f"\n\nThe customer has uploaded and analyzed a furniture image. "
            f"Detected: {image_hint.get('furniture_type', 'furniture')} "
            f"in {image_hint.get('style', 'modern')} style. "
            f"Material: {image_hint.get('primary_material', 'wood')}. "
            f"Finish: {image_hint.get('color_finish', 'natural')}. "
            f"Key features: {image_hint.get('key_features', 'standard')}. "
            f"Closest catalog match: {image_hint.get('similar_products', 'office furniture')}. "
            f"Use this as context — the customer is likely interested in "
            f"something similar to what they uploaded. "
            f"Reference the image details naturally in your response "
            f"rather than asking them to describe it again."
        )
        system_prompt += image_context
        logger.info("NODE | Reasoning | image_spec_hint injected into context")

    try:
        response_text = call_llm(user_content, system=system_prompt, temperature=0.6)
        logger.info("NODE | Reasoning | Generated response")
    except Exception as e:
        logger.error(f"NODE | Reasoning | Error: {e}\n{traceback.format_exc()}")
        response_text = "I'm having trouble thinking right now. Please try again."

    logger.info("NODE | Reasoning | EXIT")

    return {
        **state,
        "reasoning_output": response_text,
        "current_node": "reasoning",
    }
