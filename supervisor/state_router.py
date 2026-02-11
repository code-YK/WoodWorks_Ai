from schemas.base.enums import WorkflowState


def get_next_action(state: WorkflowState) -> str | None:
    """
    Decides what should happen next based on workflow state.
    Returns an ACTION, not an agent execution.
    """

    if state == WorkflowState.SESSION_STARTED:
        return "RUN_AGENT_1_USER"

    if state == WorkflowState.USER_REGISTERED:
        return "ASK_PRODUCT_SELECTION"

    if state == WorkflowState.PRODUCT_SELECTED:
        return "RUN_AGENT_2_HUMAN_REQUIREMENTS"

    if state == WorkflowState.HUMAN_REQUIREMENTS_CONFIRMED:
        return "RUN_AGENT_3_TECH_SPEC"

    if state == WorkflowState.TECH_SPEC_FINALIZED:
        return "RUN_AGENT_4_PRICING"

    if state == WorkflowState.ORDER_CONFIRMED:
        return None  

    return None
