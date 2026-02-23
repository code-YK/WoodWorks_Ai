import traceback
import logging
from graph.state import WoodWorksState

logger = logging.getLogger(__name__)


def store_chat_summary_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | StoreChatSummary | ENTER")

    assistant_response = state.get("assistant_response", "")

  
    # Previously this ran even after reasoning crashed, writing empty records.
    if not assistant_response or assistant_response.strip() == "":
        logger.warning("NODE | StoreChatSummary | Skipping — no response to store")
        return state

    new_history_item = {"role": "assistant", "content": assistant_response}
    _existing_history = state.get("conversation_history") or []

    try:
        # Placeholder for long-term DB persistence (e.g. workflow_memory table)
        # db.store_chat_turn(user_msg=..., assistant_msg=assistant_response)
        logger.info(f"NODE | StoreChatSummary | Stored response ({len(assistant_response)} chars)")
    except Exception as e:
        logger.error(f"NODE | StoreChatSummary | DB write failed: {e}\n{traceback.format_exc()}")
        # Non-fatal — state is still updated even if DB write fails

    logger.info("NODE | StoreChatSummary | EXIT")
    return {
        **state,
        "conversation_history": _existing_history + [new_history_item],
    }
