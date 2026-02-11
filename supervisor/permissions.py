from schemas.base.enums import WorkflowState

# Which agent is allowed to act in which state
AGENT_PERMISSIONS: dict[str, set[WorkflowState]] = {
    "agent_1_user": {
        WorkflowState.SESSION_STARTED,
    },
    "agent_2_human_spec": {
        WorkflowState.PRODUCT_SELECTED,
        WorkflowState.HUMAN_REQUIREMENTS_DRAFT,
    },
    "agent_3_tech_spec": {
        WorkflowState.HUMAN_REQUIREMENTS_CONFIRMED,
        WorkflowState.TECHNICAL_VALIDATION,
    },
    "agent_4_pricing": {
        WorkflowState.TECH_SPEC_FINALIZED,
        WorkflowState.PRICING_AND_STOCK_EVALUATION,
    },
}


def agent_can_act(agent_name: str, state: WorkflowState) -> bool:
    return state in AGENT_PERMISSIONS.get(agent_name, set())
