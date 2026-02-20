import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


def technical_spec_agent_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | TechnicalSpecAgent | ENTER")

    product = state.get("selected_product", {})
    human_spec = state.get("human_spec", {})

    prompt = load_prompt(
        "technical_spec.txt",
        product_name=product.get("name", ""),
        category=product.get("category", ""),
        material=product.get("material", ""),
        human_spec=json.dumps(human_spec, indent=2),
    )

    try:
        response = call_llm(prompt, json_mode=True, temperature=0.2)
        data = json.loads(response)
        logger.info("NODE | TechnicalSpecAgent | spec generated successfully")
    except Exception as e:
        logger.error(f"NODE | TechnicalSpecAgent | LLM error: {e}")
        return {
            **state,
            "supervisor_issue": f"Technical spec generation failed: {e}",
        }

    logger.info("NODE | TechnicalSpecAgent | EXIT")
    return {
        **state,
        "technical_spec": data,
        "assistant_response": (
            "Technical specification prepared. Checking stock and calculating your final price now..."
        ),
        "current_node": "technical_spec_agent",
    }
