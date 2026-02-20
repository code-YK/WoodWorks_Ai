import traceback
import logging
from graph.state import WoodWorksState

logger = logging.getLogger(__name__)


def response_generator_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | ResponseGenerator | ENTER")

    raw_response = state.get("reasoning_output", "")

    # BUG 3 FIX: Guard against empty reasoning_output (e.g. reasoning node crashed).
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

    logger.info("NODE | ResponseGenerator | EXIT")
    return {
        **state,
        "assistant_response": final_response,
        "current_node": "response_generator",
    }
