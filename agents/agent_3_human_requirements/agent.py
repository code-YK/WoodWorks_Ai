from app_log.logger import get_logger
from schemas.agent_state import AgentState
from schemas.base.enums import WorkflowState, FieldValueType
from schemas.human_requirements.field import HumanRequirementField
from schemas.human_requirements.requirements import HumanRequirements
from schemas.exceptions.validation_error import ValidationException
from integrations.llm.llm import get_llm
import json

logger = get_logger("agent_3_human_requirements")


class Agent3HumanRequirements:
    """
    Agent-3: Hybrid Human Requirements Agent
    Works on the latest selected product (multi-product compatible)
    """

    def run(
        self,
        state: AgentState,
        user_input: dict | None = None,
    ) -> AgentState:

        logger.debug(
            "Agent-3 (Human Requirements) started",
            extra={"state": state.workflow_state},
        )

        try:
            # State Guard
            if state.workflow_state != WorkflowState.PRODUCT_SELECTED:
                raise ValueError(
                    f"Human Requirements agent cannot run in state {state.workflow_state}"
                )

            if not state.product_contexts:
                raise ValidationException(
                    message="No product selected",
                    field="product_contexts",
                )

            # Work on latest product
            current_product = state.product_contexts[-1]

            # Step 1: Structured defaults
            hr_data = {
                "usage": None,
                "load_requirement": None,
                "environment": None,
                "safety_priority": False,
                "aesthetic_focus": False,
            }

            if user_input:
                hr_data.update(user_input)

            # Step 2: Detect ambiguity
            needs_llm = any(v is None for v in hr_data.values())

            if needs_llm:
                logger.info("Human requirements incomplete, invoking LLM")

                llm = get_llm()

                prompt = f"""
                    You MUST return STRICT JSON only.

                    Product category: {current_product.category}
                    Product variant: {current_product.variant}

                    Return JSON in this exact format:

                    {{
                    "usage": "...",
                    "load_requirement": "...",
                    "environment": "...",
                    "safety_priority": true/false,
                    "aesthetic_focus": true/false
                    }}

                    Do not add explanation.
                    Do not add text.
                    Return JSON only.
                """

                response = llm.invoke(prompt)

                try:
                    inferred = json.loads(response.content)
                except json.JSONDecodeError:
                    logger.error("LLM returned invalid JSON", extra={"raw": response.content})
                    raise ValueError("LLM did not return valid JSON")

                for key in hr_data:
                    if hr_data[key] is None:
                        hr_data[key] = inferred.get(key)

            # Step 3: Validate & finalize

            human_req = HumanRequirements(
                fields=[
                    HumanRequirementField(
                        key="usage",
                        label="Intended Usage",
                        value=hr_data["usage"],
                        value_type=FieldValueType.STRING,
                        required=True,
                    ),
                    HumanRequirementField(
                        key="load_requirement",
                        label="Load Requirement",
                        value=hr_data["load_requirement"],
                        value_type=FieldValueType.STRING,
                        required=True,
                    ),
                    HumanRequirementField(
                        key="environment",
                        label="Environment",
                        value=hr_data["environment"],
                        value_type=FieldValueType.STRING,
                        required=True,
                    ),
                    HumanRequirementField(
                        key="safety_priority",
                        label="Safety Priority",
                        value=hr_data["safety_priority"],
                        value_type=FieldValueType.BOOLEAN,
                        required=False,
                    ),
                    HumanRequirementField(
                        key="aesthetic_focus",
                        label="Aesthetic Focus",
                        value=hr_data["aesthetic_focus"],
                        value_type=FieldValueType.BOOLEAN,
                        required=False,
                    ),
                ]
            )


            state.human_requirements = human_req
            state.workflow_state = WorkflowState.HUMAN_REQUIREMENTS_CONFIRMED

            logger.info(
                "Human requirements confirmed",
                extra={
                    "product_id": current_product.product_id,
                    "requirements": hr_data,
                },
            )

            return state

        except Exception:
            logger.exception("Human requirements agent failed")
            raise
