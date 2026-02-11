from sqlalchemy.orm import Session

from app_log.logger import get_logger
from schemas.agent_state import AgentState
from schemas.product.product_context import ProductContext
from schemas.base.enums import WorkflowState

from agents.agent_2_product.schema import ProductSelectionInput

logger = get_logger("agent_2_product")


class Agent2Product:
    """
    Agent-2: Product Selection Agent
    Responsible for selecting product(s) and updating agent state
    """

    def __init__(self, db: Session):
        self.db = db  # kept for future validation, not used now

    def run(
        self,
        state: AgentState,
        product_input: ProductSelectionInput,
    ) -> AgentState:
        logger.debug(
            "Agent-2 started",
            extra={"workflow_state": state.workflow_state},
        )

        try:
            # State Guard
            if state.workflow_state != WorkflowState.USER_REGISTERED:
                logger.error(
                    "Agent-2 invoked in invalid state",
                    extra={"state": state.workflow_state},
                )
                raise ValueError(
                    f"Agent-2 cannot run in state {state.workflow_state}"
                )

            # Initialize product list if first product
            if state.product_contexts is None:
                state.product_contexts = []

            # Build product context
            product_context = ProductContext(
                product_id=product_input.product_id,
                category=product_input.category,
                variant=product_input.variant,
            )

            state.product_contexts.append(product_context)

            # Update workflow state
            state.workflow_state = WorkflowState.PRODUCT_SELECTED

            logger.info(
                "Product selected",
                extra={
                    "product_id": product_context.product_id,
                    "category": product_context.category,
                    "total_products": len(state.product_contexts),
                },
            )

            return state

        except Exception:
            logger.exception("Agent-2 failed")
            raise
