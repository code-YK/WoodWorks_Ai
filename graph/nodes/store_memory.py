import json
import logging
from graph.state import WoodWorksState
from tools.db_tools import store_workflow_memory

logger = logging.getLogger(__name__)


def store_memory_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | StoreMemory | ENTER")

    user_id = state.get("user_id")
    product = state.get("selected_product", {})
    product_id = product.get("product_id") if product else None
    pricing = state.get("pricing_summary", {})
    technical_spec = state.get("technical_spec", {})
    human_spec = state.get("human_spec", {})

    agent_summary = (
        f"Order completed for {state.get('user_info', {}).get('name', 'Unknown')}. "
        f"Product: {product.get('name', 'N/A')}. "
        f"Total: ${pricing.get('total_price', 0):,.2f}. "
        f"Tech summary: {technical_spec.get('summary', 'N/A')}"
    )

    final_state_snapshot = {
        "order_id": state.get("order_id"),
        "product": product,
        "human_spec": human_spec,
        "technical_spec": technical_spec,
        "pricing": pricing,
        "stock_status": state.get("stock_status"),
    }

    try:
        memory_id = store_workflow_memory(
            user_id=user_id,
            product_id=product_id,
            session_type="workflow",
            agent_summary=agent_summary,
            final_state=final_state_snapshot,
            pricing=pricing.get("total_price"),
        )
        logger.info(f"NODE | StoreMemory | memory stored | id={memory_id}")
    except Exception as e:
        logger.error(f"NODE | StoreMemory | failed to store memory: {e}")

    logger.info("NODE | StoreMemory | EXIT")
    return {
        **state,
        "workflow_complete": True,
        "current_node": "store_memory",
    }
