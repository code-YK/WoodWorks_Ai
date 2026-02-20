import logging
import json
from graph.state import WoodWorksState
from tools.fulfillment_tools import generate_receipt_tool

logger = logging.getLogger(__name__)


def generate_receipt_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | GenerateReceipt | ENTER")

    order_id = state.get("order_id")
    user_info = state.get("user_info", {})
    product = state.get("selected_product", {})
    technical_spec = state.get("technical_spec", {})
    pricing = state.get("pricing_summary", {})
    human_spec = state.get("human_spec", {})

    user_name = user_info.get("name", "Customer") if user_info else "Customer"
    product_name = product.get("name", "Custom Furniture")
    tech_summary = technical_spec.get("summary", "Custom specification — see technical docs.")
    final_price = pricing.get("total_price", 0.0)
    
    # Ensure human_spec is string for the tool
    if isinstance(human_spec, dict):
        human_spec_str = human_spec.get("raw_answers", json.dumps(human_spec, indent=2))
    else:
        human_spec_str = str(human_spec)

    try:
        # Invoke bound tool
        receipt_path = generate_receipt_tool.invoke({
            "order_id": order_id,
            "user_name": user_name,
            "product_name": product_name,
            "technical_summary": tech_summary,
            "final_price": final_price,
            "human_spec": human_spec_str,
        })
        
        logger.info(f"NODE | GenerateReceipt | Tool Success | path={receipt_path}")

    except Exception as e:
        logger.error(f"NODE | GenerateReceipt | Tool Error: {e}")
        receipt_path = None
    
    success_message = (
        f"✅ **Order #{order_id} Confirmed!**\n\n"
        f"Your order for **{product_name}** has been successfully placed.\n"
        f"Total: **${final_price:,.2f}**\n\n"
        f"Your PDF receipt is ready for download below. Our team will be in touch within 2 business days!"
    )

    logger.info("NODE | GenerateReceipt | EXIT")
    _existing_history = state.get("conversation_history") or []
    return {
        **state,
        "receipt_path": receipt_path,
        "assistant_response": success_message,
        "current_node": "generate_receipt",
        "conversation_history": _existing_history + [{"role": "assistant", "content": success_message}],
    }
