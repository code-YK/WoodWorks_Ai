import traceback
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


def query_refinement_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | QueryRefinement | ENTER")
    user_message = state.get("user_message", "")
    history = state.get("conversation_history") or []

    # BUG 2 FIX: Always run the LLM — never skip refinement for empty history.
    # The first message is when refinement matters most; empty history just means
    # it's the start of a conversation.
    if history:
        history_str = "\n".join([
            f"{m['role'].capitalize()}: {m['content']}"
            for m in history
        ])
    else:
        history_str = "No prior conversation."

    prompt = load_prompt(
        "query_refinement.txt",
        user_message=user_message,
        conversation_history=history_str,
    )

    try:
        refined_query = call_llm(prompt, temperature=0.3)
        logger.info(f"NODE | QueryRefinement | Refined: {refined_query[:80]}")
    except Exception as e:
        logger.error(f"NODE | QueryRefinement | Error: {e}\n{traceback.format_exc()}")
        refined_query = user_message  # safe fallback — pass raw message forward

    logger.info("NODE | QueryRefinement | EXIT")
    return {
        **state,
        "refined_query": refined_query,
        "current_node": "query_refinement",
    }
