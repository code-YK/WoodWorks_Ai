import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

# BUG 2 FIX: Use the proper TypedDict key declared in WoodWorksState.
# The old private string key "_human_spec_question_asked" was not in the TypedDict,
# so LangGraph silently dropped it between turns — Stage 2 never ran.
_QUESTION_ASKED_KEY = "human_spec_question_asked"


def human_spec_agent_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | HumanSpecAgent | ENTER")

    product = state.get("selected_product", {})
    user_info = state.get("user_info", {})
    user_name = user_info.get("name", "there") if user_info else "there"

    question_asked = state.get(_QUESTION_ASKED_KEY, False)
    user_message = state.get("user_message", "")

    if not question_asked:
        # Stage 1: Generate questions
        logger.info("NODE | HumanSpecAgent | Stage 1 - Generating questions")
        prompt = load_prompt(
            "human_spec_questions.txt",
            user_name=user_name,
            product_name=product.get("name", "the product"),
            category=product.get("category", ""),
            material=product.get("material", ""),
            finish_options=product.get("finish_options", ""),
            dimensions_guide=product.get("dimensions_guide", ""),
            description=product.get("description", ""),
        )
        try:
            questions_message = call_llm(prompt, temperature=0.5)
        except Exception as e:
            logger.error(f"NODE | HumanSpecAgent | LLM error generating questions: {e}")
            questions_message = "Could you please share the dimensions, finish preference, and any special requirements for your order?"

        logger.info("NODE | HumanSpecAgent | questions generated, awaiting user response")
        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            _QUESTION_ASKED_KEY: True,   # persists correctly via TypedDict
            "assistant_response": questions_message,
            "current_node": "human_spec_agent",
            "conversation_history": _existing_history + [{"role": "assistant", "content": questions_message}],
        }
    else:
        # Stage 2: Extract specs from user response
        logger.info("NODE | HumanSpecAgent | Stage 2 - Extracting specs")
        prompt = load_prompt(
            "human_spec_extraction.txt",
            product_name=product.get("name", "the product"),
            finish_options=product.get("finish_options", ""),
            dimensions_guide=product.get("dimensions_guide", ""),
            user_response=user_message,
        )
        try:
            response = call_llm(prompt, json_mode=True)
            data = json.loads(response)
        except Exception as e:
            logger.error(f"NODE | HumanSpecAgent | LLM extraction error: {e}")
            return {
                **state,
                "supervisor_issue": f"Failed to extract specs from user response: {e}",
            }

        missing = data.get("missing_critical_info", False)
        if missing:
            logger.warning(f"NODE | HumanSpecAgent | missing critical fields: {data.get('missing_fields')}")
            return {
                **state,
                "supervisor_issue": f"Missing critical specification fields: {data.get('missing_fields')}",
            }

        logger.info("NODE | HumanSpecAgent | specs extracted successfully")
        confirmation_msg = (
            f"Perfect! I've captured all your specifications for the **{product.get('name')}**. "
            f"Let me now prepare the technical specification and pricing for you."
        )
        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "human_spec": data,
            _QUESTION_ASKED_KEY: False,   # reset for future orders
            "assistant_response": confirmation_msg,
            "current_node": "human_spec_agent",
            "conversation_history": _existing_history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": confirmation_msg},
            ],
        }
