import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


def intent_decider_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | IntentDecider | ENTER")

    # Once workflow mode is set, it stays locked until the session is explicitly reset.
    if state.get("mode") == "workflow":
        logger.info("NODE | IntentDecider | mode=workflow (locked) — skipping LLM classification")
        return {**state, "current_node": "intent_decider"}

    user_message = state.get("user_message", "")

    prompt = load_prompt("intent_decider.txt", user_message=user_message)

    try:
        response = call_llm(prompt, json_mode=True)
        data = json.loads(response)
        mode = data.get("mode", "chat")
        logger.info(f"NODE | IntentDecider | mode={mode} confidence={data.get('confidence')}")
    except Exception as e:
        logger.error(f"NODE | IntentDecider | LLM error: {e}")
        mode = "chat"

   
    updates = {
        "mode": mode,
        "current_node": "intent_decider",
    }

    logger.info("NODE | IntentDecider | EXIT")
    return {**state, **updates}
