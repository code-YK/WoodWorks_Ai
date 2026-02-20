import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt
from tools.db_tools import check_inventory, get_available_products

logger = logging.getLogger(__name__)


def stock_pricing_agent_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | StockPricingAgent | ENTER")

    product = state.get("selected_product", {})
    human_spec = state.get("human_spec", {})
    technical_spec = state.get("technical_spec", {})
    quantity = human_spec.get("quantity", 1) if human_spec else 1
    product_id = product.get("product_id")

    # Step 1: Check inventory
    try:
        stock_result = check_inventory(product_id=product_id, quantity=quantity)
        logger.info(f"NODE | StockPricingAgent | stock check: {stock_result}")
    except Exception as e:
        logger.error(f"NODE | StockPricingAgent | stock check error: {e}")
        stock_result = {"available": False, "quantity_in_stock": 0, "requested_quantity": quantity, "sku": None}

    if not stock_result["available"]:
        logger.warning(f"NODE | StockPricingAgent | insufficient stock for product_id={product_id}")
        return {
            **state,
            "stock_status": stock_result,
            "supervisor_issue": (
                f"Insufficient stock for {product.get('name')}. "
                f"Requested: {quantity}, Available: {stock_result['quantity_in_stock']}"
            ),
            "current_node": "stock_pricing_agent",
        }

    # Step 2: Calculate pricing
    prompt = load_prompt(
        "pricing.txt",
        product_name=product.get("name", ""),
        base_price=product.get("base_price", 0),
        quantity=quantity,
        technical_spec=json.dumps(technical_spec, indent=2),
        human_spec=json.dumps(human_spec, indent=2),
    )

    try:
        response = call_llm(prompt, json_mode=True, temperature=0.1)
        pricing_data = json.loads(response)
        logger.info(f"NODE | StockPricingAgent | pricing calculated: total=${pricing_data.get('total_price')}")
    except Exception as e:
        logger.error(f"NODE | StockPricingAgent | pricing LLM error: {e}")
        # Fallback pricing
        pricing_data = {
            "base_price": product.get("base_price", 0),
            "customization_cost": 0,
            "material_cost": 0,
            "total_price": product.get("base_price", 0) * quantity,
            "breakdown": "Standard pricing applied.",
        }

    logger.info("NODE | StockPricingAgent | EXIT")
    total = pricing_data.get('total_price', 0)
    breakdown = pricing_data.get('breakdown', '')
    return {
        **state,
        "stock_status": stock_result,
        "pricing_summary": pricing_data,
        "assistant_response": (
            f"Stock confirmed. Your total is **${total:,.2f}**.\n\n"
            f"{breakdown}\n\n"
            f"Click **Confirm Order** below when you're ready to proceed."
        ),
        "current_node": "stock_pricing_agent",
    }
