from pydantic import BaseModel
from typing import List

from schemas.base.enums import WorkflowState
from schemas.user.user_context import UserContext
from schemas.product.product_context import ProductContext
from schemas.human_requirements.requirements import HumanRequirements
from schemas.technical_spec.specification import TechnicalSpecification
from schemas.pricing.pricing_context import PricingContext
from schemas.confirmation.confirmation_flags import ConfirmationFlags
from schemas.exceptions.validation_error import ValidationException


class AgentState(BaseModel):
    workflow_state: WorkflowState = WorkflowState.SESSION_STARTED

    user_context: UserContext | None = None

    product_contexts: List[ProductContext] | None = None

    human_requirements: HumanRequirements | None = None
    technical_spec: TechnicalSpecification | None = None
    pricing_context: PricingContext | None = None

    confirmation: ConfirmationFlags = ConfirmationFlags()
    exception: ValidationException | None = None
