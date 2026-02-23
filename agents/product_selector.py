import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt
from tools.db_tools import get_available_products

logger = logging.getLogger(__name__)


def _format_products_list(products: list) -> str:
    lines = []
    for p in products:
        lines.append(
            f"ID:{p['product_id']} | {p['name']} | {p['category']} | "
            f"${p['base_price']:,.2f} | Material: {p['material']} | Stock: {p['stock_quantity']}"
        )
    return "\n".join(lines)


def product_selector_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | ProductSelector | ENTER")
    user_message = state.get("user_message", "")
    user_info = state.get("user_info", {})
    user_name = user_info.get("name", "there") if user_info else "there"

    try:
        products = get_available_products()
    except Exception as e:
        logger.error(f"NODE | ProductSelector | DB error fetching products: {e}")
        return {**state, "assistant_response": "Unable to fetch products. Please try again.", "error": str(e)}

    products_list = _format_products_list(products)

    # ── Image hint (vision feature) ──────────────────────────────────────
    image_hint = state.get("image_spec_hint")
    image_hint_str = ""
    if image_hint:
        image_hint_str = (
            f"IMPORTANT: Customer uploaded a reference image. "
            f"Detected furniture type: {image_hint.get('furniture_type')}. "
            f"Style: {image_hint.get('style_hint')}. "
            f"Material: {image_hint.get('material_hint')}. "
            f"Auto-select the closest matching product from the catalog "
            f"without asking the customer to confirm — set selected=true "
            f"and include a message telling them what was matched."
        )
        logger.info(f"NODE | ProductSelector | image_spec_hint present: "
                    f"{image_hint.get('furniture_type')}")

    prompt = load_prompt(
        "product_selector.txt",
        products_list=products_list,
        user_name=user_name,
        user_message=user_message,
        image_hint=image_hint_str,
    )

    try:
        response = call_llm(prompt, json_mode=True)
        data = json.loads(response)
    except Exception as e:
        logger.error(f"NODE | ProductSelector | LLM error: {e}")
        return {**state, "assistant_response": "I had trouble processing that. Could you tell me which product you're interested in?"}

    message_to_user = data.get("message_to_user", "")

    if data.get("selected"):
        product_id = data.get("product_id")
        # Find full product details
        selected = next((p for p in products if p["product_id"] == product_id), None)
        if not selected:
            logger.warning(f"NODE | ProductSelector | product_id={product_id} not found in catalog")
            return {**state, "assistant_response": message_to_user}

        logger.info(f"NODE | ProductSelector | selected product_id={product_id} name={selected['name']}")
        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "selected_product": selected,
            "assistant_response": message_to_user,
            "current_node": "product_selector",
            "conversation_history": _existing_history + [{"role": "assistant", "content": message_to_user}],
        }
    else:
        logger.info("NODE | ProductSelector | awaiting product selection")
        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "assistant_response": message_to_user,
            "current_node": "product_selector",
            "conversation_history": _existing_history + [{"role": "assistant", "content": message_to_user}],
        }
