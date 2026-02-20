import json
import logging
import traceback
from datetime import datetime, timedelta
from graph.state import WoodWorksState
from tools.fulfillment_tools import create_order_tool

logger = logging.getLogger(__name__)


def create_order_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | CreateOrder | ENTER")

    if not state.get("confirmed_by_user"):
        logger.warning("NODE | CreateOrder | attempted without user confirmation — BLOCKED")
        return {
            **state,
            "assistant_response": "Order cannot be created without explicit confirmation.",
            "supervisor_issue": "Order attempted without confirmation",
        }

    user_id = state.get("user_id")
    product = state.get("selected_product", {})
    human_spec = state.get("human_spec", {})
    technical_spec = state.get("technical_spec", {})
    pricing = state.get("pricing_summary", {})

    product_id = product.get("product_id")
    final_price = pricing.get("total_price", 0.0)
    human_spec_str = json.dumps(human_spec, indent=2)
    tech_spec_str = json.dumps(technical_spec, indent=2)

    # BUG 3 FIX (Part D): database-level duplicate guard — block if an identical order
    # was already created for the same user+product within the last 60 seconds.
    try:
        from database.models import Order
        from database.session import get_session
        with get_session() as session:
            cutoff = datetime.utcnow() - timedelta(seconds=60)
            existing = (
                session.query(Order)
                .filter_by(user_id=user_id, product_id=product_id, status="confirmed")
                .filter(Order.created_at >= cutoff)
                .order_by(Order.created_at.desc())
                .first()
            )
            if existing:
                logger.warning(
                    f"NODE | CreateOrder | duplicate blocked — order_id={existing.id} "
                    f"created {datetime.utcnow() - existing.created_at:.1f}s ago"
                )
                return {
                    **state,
                    "order_id": existing.id,
                    "current_node": "create_order",
                }
    except Exception as dup_e:
        # Non-fatal — if duplicate check fails (e.g. model not yet migrated), proceed normally
        logger.warning(f"NODE | CreateOrder | duplicate check skipped: {dup_e}")

    try:
        tool_result = create_order_tool.invoke({
            "user_id": user_id,
            "product_id": product_id,
            "human_spec": human_spec_str,
            "technical_spec": tech_spec_str,
            "final_price": final_price
        })

        order_id = tool_result.get("order_id")
        logger.info(f"NODE | CreateOrder | Tool Success | order_id={order_id}")

    except Exception as e:
        logger.error(f"NODE | CreateOrder | Tool Error: {e}\n{traceback.format_exc()}")
        return {
            **state,
            "supervisor_issue": f"Order creation failed: {e}",
            "error": str(e),
        }

    return {
        **state,
        "order_id": order_id,
        "current_node": "create_order",
    }
