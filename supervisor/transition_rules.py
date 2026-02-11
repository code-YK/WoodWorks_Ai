from schemas.base.enums import WorkflowState

# Allowed forward transitions
ALLOWED_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.SESSION_STARTED: {
        WorkflowState.USER_REGISTERED,
    },
    WorkflowState.USER_REGISTERED: {
        WorkflowState.PRODUCT_SELECTED,
    },
    WorkflowState.PRODUCT_SELECTED: {
        WorkflowState.HUMAN_REQUIREMENTS_DRAFT,
    },
    WorkflowState.HUMAN_REQUIREMENTS_DRAFT: {
        WorkflowState.HUMAN_REQUIREMENTS_CONFIRMED,
    },
    WorkflowState.HUMAN_REQUIREMENTS_CONFIRMED: {
        WorkflowState.TECHNICAL_VALIDATION,
    },
    WorkflowState.TECHNICAL_VALIDATION: {
        WorkflowState.TECH_SPEC_FINALIZED,
    },
    WorkflowState.TECH_SPEC_FINALIZED: {
        WorkflowState.PRICING_AND_STOCK_EVALUATION,
    },
    WorkflowState.PRICING_AND_STOCK_EVALUATION: {
        WorkflowState.ORDER_REVIEW,
    },
    WorkflowState.ORDER_REVIEW: {
        WorkflowState.ORDER_CONFIRMED,
    },
    WorkflowState.ORDER_CONFIRMED: set(),  # terminal
}


def is_valid_transition(
    from_state: WorkflowState,
    to_state: WorkflowState,
) -> bool:
    return to_state in ALLOWED_TRANSITIONS.get(from_state, set())
