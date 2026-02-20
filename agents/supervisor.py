import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt
from tools.db_tools import get_available_products
from config.settings import MAX_SUPERVISOR_STEPS

logger = logging.getLogger(__name__)


def _build_state_summary(state: WoodWorksState) -> str:
    # Summarize what we have to help the supervisor decide what's missing
    return json.dumps({
        "mode": state.get("mode"),
        "user_info_collected": bool(state.get("user_info")),
        "product_selected": state.get("selected_product", {}).get("name") if state.get("selected_product") else None,
        "human_spec_collected": bool(state.get("human_spec")),
        "technical_spec_generated": bool(state.get("technical_spec")),
        "stock_checked": bool(state.get("stock_status")),
        "pricing_done": bool(state.get("pricing_summary")),
        "confirmed": state.get("confirmed_by_user"),
        "order_id": state.get("order_id"),
        "current_node": state.get("current_node"),
    }, indent=2)


def supervisor_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | Supervisor | ENTER")

    # Check max steps to prevent infinite loops
    steps = state.get("supervisor_steps", 0) + 1
    if steps > MAX_SUPERVISOR_STEPS:
        logger.error(f"NODE | Supervisor | max steps exceeded ({MAX_SUPERVISOR_STEPS})")
        return {
            **state,
            "supervisor_steps": steps,
            "supervisor_decision": {"next_agent": "end", "reason": "Max steps exceeded"},
            "assistant_response": "I'm sorry, we encountered too many issues processing your order. Please contact support.",
        }

    # Identify if there was a specific issue reported by a worker
    issue = state.get("supervisor_issue", None)
    state_summary = _build_state_summary(state)

    # If no issue, the "issue" is just "determine next step"
    issue_description = issue if issue else "Determine the next workflow step based on missing information."

    try:
        products = get_available_products()
        catalog_str = "\n".join([f"ID:{p['product_id']} | {p['name']} | ${p['base_price']:,.2f} | Stock:{p['stock_quantity']}" for p in products])
    except Exception:
        catalog_str = "Error loading catalog"

    prompt = load_prompt(
        "supervisor.txt",
        state_summary=state_summary,
        issue_description=issue_description,
        product_catalog=catalog_str,
    )

    try:
        response = call_llm(prompt, json_mode=True, temperature=0.1)
        decision = json.loads(response)
        logger.info(f"NODE | Supervisor | decision: next_agent={decision.get('next_agent')} reason={decision.get('reason')}")
    except Exception as e:
        logger.error(f"NODE | Supervisor | LLM error: {e}")
        # Fallback logic if LLM fails
        decision = {
            "next_agent": "end",
            "reason": f"Supervisor LLM failure: {e}",
            "message_to_user": "We encountered an internal issue. Please try again."
        }

    message_to_user = decision.get("message_to_user", "")

    updated_state = {
        **state,
        "supervisor_steps": steps,
        "supervisor_issue": None, # Clear the issue as we've handled it
        "supervisor_decision": decision,
        "current_node": "supervisor",
    }

    # If supervisor suggests an alternative product, update selected_product
    alt_product_id = decision.get("suggested_product_id")
    if alt_product_id:
        try:
            products = get_available_products()
            alt = next((p for p in products if p["product_id"] == alt_product_id), None)
            if alt:
                updated_state["selected_product"] = alt
                # Reset downstream states if product changes
                updated_state["human_spec"] = None
                updated_state["technical_spec"] = None
                updated_state["pricing_summary"] = None
                updated_state["stock_status"] = None
                logger.info(f"NODE | Supervisor | alternative product set: {alt['name']}")
        except Exception:
            pass

    if message_to_user:
        updated_state["assistant_response"] = message_to_user
        _existing_history = updated_state.get("conversation_history") or []
        updated_state["conversation_history"] = _existing_history + [{"role": "assistant", "content": message_to_user}]

    logger.info("NODE | Supervisor | EXIT")
    return updated_state
