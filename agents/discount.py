"""
Discount Agent — handles discount/negotiation requests.

Reads pricing_summary + user_message, decides whether to grant
a discount (max 10%), updates the pricing breakdown, and responds.
"""

import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm

logger = logging.getLogger(__name__)

_DISCOUNT_PROMPT = """\
You are a sales agent for WoodWorks AI premium furniture.
Product: {product_name}, Current total: ${total_price}
Customer request: "{user_message}"

Business rules:
- Maximum discount: 10%
- Only grant if customer explicitly asks
- Be warm but firm — we offer quality at fair prices
- For reasonable requests offer 5-10% goodwill discount

Respond ONLY in JSON:
{{
  "discount_granted": true/false,
  "discount_percent": 0-10,
  "discount_amount": number,
  "new_total": number,
  "message_to_user": "your response"
}}
"""


def discount_agent_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | DiscountAgent | ENTER")

    pricing = state.get("pricing_summary") or {}
    product = state.get("selected_product") or {}
    user_message = state.get("user_message", "")

    total_price = pricing.get("total_price", 0)
    product_name = product.get("name", "the product")

    prompt = _DISCOUNT_PROMPT.format(
        product_name=product_name,
        total_price=total_price,
        user_message=user_message,
    )

    try:
        response = call_llm(prompt, json_mode=True)
        data = json.loads(response)
    except Exception as e:
        logger.error(f"NODE | DiscountAgent | LLM error: {e}")
        msg = "I appreciate you asking! Unfortunately I couldn't process the discount request right now. Would you like to proceed with the current pricing?"
        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "assistant_response": msg,
            "current_node": "discount_agent",
            "discount_applied": {"discount_granted": False, "error": str(e)},
            "conversation_history": _existing_history + [{"role": "assistant", "content": msg}],
        }

    granted = data.get("discount_granted", False)
    message_to_user = data.get("message_to_user", "")

    if granted:
        new_total = data.get("new_total", total_price)
        discount_pct = data.get("discount_percent", 0)
        discount_amt = data.get("discount_amount", 0)

        # Update pricing_summary with discount
        updated_pricing = dict(pricing)
        updated_pricing["total_price"] = new_total
        breakdown = updated_pricing.get("breakdown", "")
        updated_pricing["breakdown"] = (
            f"{breakdown}\n"
            f"Discount ({discount_pct}%): -${discount_amt:,.2f}\n"
            f"New Total: ${new_total:,.2f}"
        )

        logger.info(
            f"NODE | DiscountAgent | granted={granted} percent={discount_pct}% "
            f"new_total=${new_total}"
        )

        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "pricing_summary": updated_pricing,
            "assistant_response": message_to_user,
            "current_node": "discount_agent",
            "discount_applied": data,
            "conversation_history": _existing_history + [{"role": "assistant", "content": message_to_user}],
        }
    else:
        logger.info("NODE | DiscountAgent | granted=False percent=0% new_total=$%s", total_price)
        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "assistant_response": message_to_user,
            "current_node": "discount_agent",
            "discount_applied": data,
            "conversation_history": _existing_history + [{"role": "assistant", "content": message_to_user}],
        }
