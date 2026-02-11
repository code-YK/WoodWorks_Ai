from app_log.logger import get_logger
from schemas.agent_state import AgentState
from schemas.base.enums import WorkflowState, FieldValueType
from schemas.technical_spec.specification import TechnicalSpecification
from schemas.technical_spec.field import TechnicalSpecField
from schemas.exceptions.validation_error import ValidationException

logger = get_logger("agent_4_tech_spec")


class Agent4TechSpec:
    """
    Agent-4: Converts Human Requirements (dynamic fields)
    into Technical Specification (dynamic fields).
    """

    def run(self, state: AgentState) -> AgentState:

        logger.debug(
            "Agent-4 (Tech Spec) started",
            extra={"state": state.workflow_state},
        )

        try:
            if state.workflow_state != WorkflowState.HUMAN_REQUIREMENTS_CONFIRMED:
                raise ValueError(
                    f"Tech Spec agent cannot run in state {state.workflow_state}"
                )

            if not state.human_requirements:
                raise ValidationException(
                    message="Human requirements missing",
                    field="human_requirements",
                )

            hr = state.human_requirements

            # Helper: extract field
            def get_field_value(key: str):
                for f in hr.fields:
                    if f.key == key:
                        return f.value
                return None

            load = get_field_value("load_requirement")
            environment = get_field_value("environment")
            material_pref = get_field_value("material_preference")
            finish_pref = get_field_value("finish_preference")
            safety = get_field_value("safety_priority")

            thickness = 18 if str(load).upper() == "HEAVY" else 12
            waterproof = str(environment).upper() == "KITCHEN"

            material = material_pref if material_pref else "PLYWOOD"
            finish = finish_pref if finish_pref else "LAMINATE"

            tech_spec = TechnicalSpecification(
                fields=[
                    TechnicalSpecField(
                        key="material",
                        label="Material",
                        value=material,
                        value_type=FieldValueType.STRING,
                        required=True,
                    ),
                    TechnicalSpecField(
                        key="finish",
                        label="Finish",
                        value=finish,
                        value_type=FieldValueType.STRING,
                        required=True,
                    ),
                    TechnicalSpecField(
                        key="thickness_mm",
                        label="Thickness",
                        value=thickness,
                        value_type=FieldValueType.NUMBER,
                        unit="mm",
                        required=True,
                    ),
                    TechnicalSpecField(
                        key="waterproof",
                        label="Waterproof",
                        value=waterproof,
                        value_type=FieldValueType.BOOLEAN,
                        required=False,
                    ),
                    TechnicalSpecField(
                        key="fire_resistant",
                        label="Fire Resistant",
                        value=bool(safety),
                        value_type=FieldValueType.BOOLEAN,
                        required=False,
                    ),
                ]
            )

            state.technical_spec = tech_spec
            state.workflow_state = WorkflowState.TECH_SPEC_FINALIZED

            logger.info(
                "Technical specification finalized",
                extra={
                    "material": material,
                    "thickness": thickness,
                },
            )

            return state

        except Exception as e:
            logger.exception("Tech Spec agent failed", exc_info=e)
            raise
