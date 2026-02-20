import logging
from graph.state import WoodWorksState

logger = logging.getLogger(__name__)


def final_confirmation_node(state: WoodWorksState) -> WoodWorksState:
    """
    Hard gate — builds confirmation message for user.
    Actual confirmation is set by the UI via confirmed_by_user flag.
    """
    logger.info("NODE | FinalConfirmation | ENTER")

    product = state.get("selected_product", {})
    pricing = state.get("pricing_summary", {})
    technical_spec = state.get("technical_spec", {})
    human_spec = state.get("human_spec", {})
    user_info = state.get("user_info", {})

    product_name = product.get("name", "N/A")
    total_price = pricing.get("total_price", 0.0)
    breakdown = pricing.get("breakdown", "")
    tech_summary = technical_spec.get("summary", "")
    lead_days = technical_spec.get("estimated_lead_days", "TBD")
    user_name = user_info.get("name", "Customer") if user_info else "Customer"
    quantity = human_spec.get("quantity", 1) if human_spec else 1

    confirmation_message = (
        f"📋 **Order Summary for {user_name}**\n\n"
        f"**Product:** {product_name}\n"
        f"**Quantity:** {quantity}\n\n"
        f"**Technical Overview:**\n{tech_summary}\n\n"
        f"**Pricing:**\n{breakdown}\n\n"
        f"**Total Price: ${total_price:,.2f}**\n"
        f"**Estimated Lead Time:** {lead_days} business days\n\n"
        f"---\n"
        f"Please confirm your order by clicking **Confirm Order** below, or type 'cancel' to start over."
    )

    logger.info(f"NODE | FinalConfirmation | confirmation shown | total=${total_price}")
    logger.info("NODE | FinalConfirmation | EXIT")

    _existing_history = state.get("conversation_history") or []
    return {
        **state,
        "confirmation_status": True,
        "assistant_response": confirmation_message,
        "current_node": "final_confirmation",
        "conversation_history": _existing_history + [{"role": "assistant", "content": confirmation_message}],
    }
