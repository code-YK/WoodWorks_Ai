import traceback
import logging
from graph.state import WoodWorksState

logger = logging.getLogger(__name__)


def response_generator_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | ResponseGenerator | ENTER")

    raw_response = state.get("reasoning_output", "")

    
    # Without this, the user sees a blank response with no explanation.
    if not raw_response or raw_response.strip() == "":
        logger.warning("NODE | ResponseGenerator | reasoning_output is empty — using fallback")
        fallback = (
            "I'm sorry, I had trouble processing that. "
            "Could you rephrase your question?"
        )
        return {
            **state,
            "assistant_response": fallback,
            "current_node": "response_generator",
        }

    # Formatting / post-processing can be added here in the future
    final_response = raw_response

    # ── Image context enrichment (vision feature) ───────────────────────
    image_hint = state.get("image_spec_hint")
    if image_hint and final_response:
        final_response += (
            f"\n\n*Based on your uploaded image of a "
            f"{image_hint.get('furniture_type', 'furniture piece')}, "
            f"I can help you start a custom order — just say "
            f"\"I'd like to place an order\" whenever you're ready!*"
        )
        logger.info("NODE | ResponseGenerator | appended image-based order nudge")

    logger.info("NODE | ResponseGenerator | EXIT")
    return {
        **state,
        "assistant_response": final_response,
        "current_node": "response_generator",
    }
