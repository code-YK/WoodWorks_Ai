import json
import logging
from graph.state import WoodWorksState
from llm.groq_client import call_llm
from agents.prompt_loader import load_prompt
from tools.db_tools import create_user

logger = logging.getLogger(__name__)


def user_info_collector_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | UserInfoCollector | ENTER")
    user_message = state.get("user_message", "")

    prompt = load_prompt("user_info.txt", user_message=user_message)

    try:
        response = call_llm(prompt, json_mode=True)
        data = json.loads(response)
    except Exception as e:
        logger.error(f"NODE | UserInfoCollector | LLM error: {e}")
        return {
            **state,
            "assistant_response": "Welcome to WoodWorks AI! Could you please share your name to get started?",
            "current_node": "user_info_collector",
        }

    message_to_user = data.get("message_to_user", "")

    if data.get("collected"):
        name = data.get("name", "Customer")
        email = data.get("email")
        phone = data.get("phone")

        try:
            user_id = create_user(name=name, email=email, phone=phone)
        except Exception as e:
            logger.error(f"NODE | UserInfoCollector | DB error: {e}")
            user_id = None

        user_info = {"name": name, "email": email, "phone": phone, "user_id": user_id}
        logger.info(f"NODE | UserInfoCollector | user collected: {name} id={user_id}")

        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "user_info": user_info,
            "user_id": user_id,
            "assistant_response": message_to_user,
            "current_node": "user_info_collector",
            "conversation_history": _existing_history + [{"role": "assistant", "content": message_to_user}],
        }
    else:
        logger.info("NODE | UserInfoCollector | awaiting user name")
        _existing_history = state.get("conversation_history") or []
        return {
            **state,
            "assistant_response": message_to_user,
            "current_node": "user_info_collector",
            "conversation_history": _existing_history + [{"role": "assistant", "content": message_to_user}],
        }
