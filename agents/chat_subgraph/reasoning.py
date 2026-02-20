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

    # BUG 2 FIX: Prefer user_message (always set fresh by app.py on every turn) as the
    # primary source of the current user input. refined_query may be stale from a previous
    # turn — only use it as a supplement when user_message isn't available.
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
        conversation_history=""  # history is context only; actual query is user_content
    )

    try:
        response_text = call_llm(user_content, system=system_prompt, temperature=0.6)
        logger.info("NODE | Reasoning | Generated response")
    except Exception as e:
        logger.error(f"NODE | Reasoning | Error: {e}\n{traceback.format_exc()}")
        response_text = "I'm having trouble thinking right now. Please try again."

    logger.info("NODE | Reasoning | EXIT")
    # BUG 1 FIX: Always return {**state, ...} to preserve all other state fields
    return {
        **state,
        "reasoning_output": response_text,
        "current_node": "reasoning",
    }
