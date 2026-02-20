"""
Short-term memory is managed entirely within LangGraph State (WoodWorksState).
This module provides helper utilities to read and update state cleanly.
"""
import logging
from typing import Dict, Any
from graph.state import WoodWorksState

logger = logging.getLogger(__name__)


def get_conversation_context(state: WoodWorksState) -> str:
    """Build a readable conversation context string from history."""
    history = state.get("conversation_history", [])
    lines = []
    for msg in history:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def clear_workflow_state(state: WoodWorksState) -> WoodWorksState:
    """Reset workflow-specific fields while keeping user session alive."""
    logger.info("SHORT_TERM_MEMORY | Clearing workflow state")
    return {
        **state,
        "selected_product": None,
        "human_spec": None,
        "technical_spec": None,
        "pricing_summary": None,
        "stock_status": None,
        "confirmation_status": False,
        "confirmed_by_user": False,
        "order_id": None,
        "receipt_path": None,
        "supervisor_issue": None,
        "supervisor_decision": None,
        "supervisor_steps": 0,
        "error": None,
        "workflow_complete": False,
    }


def get_state_summary(state: WoodWorksState) -> Dict[str, Any]:
    """Return a human-readable summary of the current state for debugging."""
    return {
        "mode": state.get("mode"),
        "current_node": state.get("current_node"),
        "user": state.get("user_info", {}).get("name") if state.get("user_info") else None,
        "product": state.get("selected_product", {}).get("name") if state.get("selected_product") else None,
        "specs_collected": bool(state.get("human_spec")),
        "technical_done": bool(state.get("technical_spec")),
        "pricing_done": bool(state.get("pricing_summary")),
        "confirmed": state.get("confirmed_by_user"),
        "order_id": state.get("order_id"),
        "complete": state.get("workflow_complete"),
    }
