from schemas.agent_state import AgentState
from schemas.base.enums import WorkflowState
from app_log.logger import get_logger

from supervisor.transition_rules import is_valid_transition
from supervisor.permissions import agent_can_act
from supervisor.state_router import get_next_action

logger = get_logger("supervisor")


class Supervisor:
    """
    Stateless workflow supervisor.
    Decides what should happen next.
    """

    def decide_next(self, state: AgentState) -> dict:
        """
        Inspects current state and returns next action.
        Does NOT execute agents.
        """

        logger.debug(
            "Supervisor decision started",
            extra={"state": state.workflow_state},
        )

        action = get_next_action(state.workflow_state)

        if not action:
            logger.info(
                "Workflow complete or paused",
                extra={"state": state.workflow_state},
            )
            return {
                "action": None,
                "state": state,
            }

        logger.info(
            "Supervisor decision made",
            extra={
                "state": state.workflow_state,
                "action": action,
            },
        )

        return {
            "action": action,
            "state": state,
        }

    def validate_transition(
        self,
        from_state: WorkflowState,
        to_state: WorkflowState,
    ):
        if not is_valid_transition(from_state, to_state):
            logger.error(
                "Invalid workflow transition",
                extra={"from": from_state, "to": to_state},
            )
            raise ValueError(
                f"Invalid transition: {from_state} → {to_state}"
            )

    def validate_agent_permission(
        self,
        agent_name: str,
        state: WorkflowState,
    ):
        if not agent_can_act(agent_name, state):
            logger.error(
                "Agent permission violation",
                extra={"agent": agent_name, "state": state},
            )
            raise PermissionError(
                f"Agent '{agent_name}' not allowed in state {state}"
            )
