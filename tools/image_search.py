"""
Image search / analysis tool for WoodWorks AI.

Provides two entry-points:
  • process_image_for_chat()     — user asks about an image in chat mode
  • process_image_for_workflow() — user uploads a reference during an order workflow
"""

import json
import logging
import os
import re

logger = logging.getLogger(__name__)

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


def _load_image_prompt() -> str:
    """Load the static image analysis prompt."""
    path = os.path.join(_PROMPTS_DIR, "image_analysis.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_json_response(raw: str) -> dict:
    """Safely parse a JSON response, stripping markdown fences if present."""
    cleaned = raw.strip()
    # Strip ```json ... ``` wrappers
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def _build_chat_response(analysis: dict) -> str:
    """Convert the structured analysis dict into a friendly natural-language
    response suitable for the chat UI."""
    ftype = analysis.get("furniture_type", "unknown")
    if ftype == "unknown":
        return (
            "I wasn't able to clearly identify the furniture in that image. "
            "Could you try uploading a clearer photo, or describe what you're looking for?"
        )

    style = analysis.get("style", "N/A")
    material = analysis.get("primary_material", "N/A")
    finish = analysis.get("color_finish", "N/A")
    dims = analysis.get("estimated_dimensions") or "not discernible from the image"
    features = analysis.get("key_features", "N/A")
    similar = analysis.get("similar_products", "N/A")
    use = analysis.get("suggested_use", "N/A")
    custom = analysis.get("customization_hints", "N/A")
    confidence = analysis.get("confidence", "N/A")

    return (
        f"📷 **Image Analysis** (confidence: {confidence})\n\n"
        f"I can see a **{ftype}** in **{style}** style.\n\n"
        f"**Materials & Finish:** {material} with {finish}\n\n"
        f"**Estimated Dimensions:** {dims}\n\n"
        f"**Key Features:** {features}\n\n"
        f"**Closest Catalog Match:** {similar}\n\n"
        f"**Suggested Use:** {use}\n\n"
        f"**Customization Ideas:** {custom}\n\n"
        f"Would you like to explore similar items from our catalog, "
        f"or start a custom order based on this design?"
    )


# ── Public API ───────────────────────────────────────────────────────────────

def process_image_for_chat(
    image_bytes: bytes,
    media_type: str,
    user_question: str = "",
) -> dict:
    """Analyze a furniture image and return a chat-friendly response.

    Always returns a dict — never raises.
    """
    logger.info("TOOL | process_image_for_chat | ENTER")

    try:
        from llm.vision_client import analyze_image
    except ValueError as e:
        # GROQ_VISION_API_KEY not set
        return {"success": False, "analysis": None, "chat_response": None,
                "error": "Vision API key not configured. Please set GROQ_VISION_API_KEY."}

    try:
        prompt = _load_image_prompt()
        if user_question:
            prompt += f"\n\nThe customer also asked: {user_question}"

        raw = analyze_image(image_bytes, media_type, prompt)
        analysis = _parse_json_response(raw)
        chat_response = _build_chat_response(analysis)

        logger.info("TOOL | process_image_for_chat | analysis complete")
        return {
            "success": True,
            "analysis": analysis,
            "chat_response": chat_response,
            "error": None,
        }

    except Exception as e:
        logger.error("TOOL | process_image_for_chat | ERROR: %s", e)
        return {
            "success": False,
            "analysis": None,
            "chat_response": None,
            "error": str(e),
        }


def process_image_for_workflow(
    image_bytes: bytes,
    media_type: str,
) -> dict:
    """Analyze a furniture image and return spec-hints for the order workflow.

    Always returns a dict — never raises.
    """
    logger.info("TOOL | process_image_for_workflow | ENTER")

    try:
        from llm.vision_client import analyze_image
    except ValueError as e:
        return {"success": False, "analysis": None, "human_spec_hint": None,
                "workflow_message": None,
                "error": "Vision API key not configured. Please set GROQ_VISION_API_KEY."}

    try:
        prompt = _load_image_prompt()
        raw = analyze_image(image_bytes, media_type, prompt)
        analysis = _parse_json_response(raw)

        # Build spec-relevant hints
        human_spec_hint = {
            "from_image": True,
            "furniture_type": analysis.get("furniture_type"),
            "style_hint": analysis.get("style"),
            "material_hint": analysis.get("primary_material"),
            "finish_hint": analysis.get("color_finish"),
            "dimension_hint": analysis.get("estimated_dimensions"),
            "feature_hints": analysis.get("key_features"),
        }

        ftype = analysis.get("furniture_type", "furniture")
        style = analysis.get("style", "")
        material = analysis.get("primary_material", "")

        workflow_message = (
            f"📷 I've analyzed your reference image! I detected a **{ftype}**"
            f"{f' in **{style}** style' if style else ''}"
            f"{f' made of **{material}**' if material else ''}.\n\n"
            f"I'll use this as a starting point for your order. "
            f"You can confirm or adjust any of these details in the next steps."
        )

        logger.info("TOOL | process_image_for_workflow | analysis complete")
        return {
            "success": True,
            "analysis": analysis,
            "human_spec_hint": human_spec_hint,
            "workflow_message": workflow_message,
            "error": None,
        }

    except Exception as e:
        logger.error("TOOL | process_image_for_workflow | ERROR: %s", e)
        return {
            "success": False,
            "analysis": None,
            "human_spec_hint": None,
            "workflow_message": None,
            "error": str(e),
        }
