from sqlalchemy.orm import Session

from app_log.logger import get_logger
from schemas.agent_state import AgentState
from schemas.db.user import UserCreate
from schemas.user.user_context import UserContext
from schemas.user.address import Address
from schemas.base.enums import WorkflowState

from integrations.database.user_repository import (
    create_user,
    get_user_by_email,
)

from agents.agent_1_user.schema import UserRegistrationInput

logger = get_logger("agent_1_user")


class Agent1User:
    """
    Agent-1: User Registration Agent
    """

    def __init__(self, db: Session):
        self.db = db

    def run(self, state: AgentState, user_input: UserRegistrationInput) -> AgentState:
        logger.debug(
            "Agent-1 started",
            extra={"workflow_state": state.workflow_state},
        )

        try:
            # State Guard
            if state.workflow_state != WorkflowState.SESSION_STARTED:
                logger.error(
                    "Agent-1 invoked in invalid state",
                    extra={"state": state.workflow_state},
                )
                raise ValueError(
                    f"Agent-1 cannot run in state {state.workflow_state}"
                )

            # Check existing user
            existing_user = get_user_by_email(self.db, user_input.email)

            if existing_user:
                logger.info(
                    "Existing user found",
                    extra={
                        "user_id": existing_user.id,
                        "email": existing_user.email,
                    },
                )

                state.user_context = UserContext(
                    id=existing_user.id,
                    name=existing_user.name,
                    email=existing_user.email,
                    phone=existing_user.phone,
                    address=Address(
                        line_1=existing_user.address_line_1,
                        line_2=existing_user.address_line_2,
                        city=existing_user.city,
                        state=existing_user.state,
                        pincode=existing_user.pincode,
                    ),
                )

            else:
                logger.info(
                    "Creating new user",
                    extra={"email": user_input.email},
                )

                user_create = UserCreate(
                    name=user_input.name,
                    email=user_input.email,
                    phone=user_input.phone,
                    address=user_input.address,
                )

                db_user = create_user(self.db, user_create)

                state.user_context = UserContext(
                    id=db_user.id,
                    name=db_user.name,
                    email=db_user.email,
                    phone=db_user.phone,
                    address=user_input.address,  # already validated Address
                )

            # Update workflow state
            state.workflow_state = WorkflowState.USER_REGISTERED

            logger.info(
                "User registration completed",
                extra={
                    "user_id": state.user_context.id,
                    "next_state": state.workflow_state,
                },
            )

            return state

        except Exception:
            logger.exception("Agent-1 failed")
            raise
