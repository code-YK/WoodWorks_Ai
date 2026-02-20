from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict



class WoodWorksState(TypedDict, total=False):
    # Meta
    mode: str                          # "chat" | "workflow"
    current_node: str
    supervisor_steps: int
    error: Optional[str]
    workflow_complete: bool

    # Conversation
    user_message: str
    # Plain list — NO operator.add reducer. History is managed explicitly.
    # Each node that writes history must build the full updated list:
    #   existing = state.get("conversation_history") or []
    #   updated  = existing + [{"role": "assistant", "content": msg}]
    conversation_history: Optional[List[Dict[str, str]]]
    assistant_response: str

    # Chat subgraph pipeline fields
    refined_query: Optional[str]          # written by query_refinement, read by reasoning
    retrieved_context: Optional[str]      # written by data_retrieval, read by reasoning
    reasoning_output: Optional[str]       # written by reasoning, read by response_generator

    # User info
    user_info: Optional[Dict[str, Any]]
    user_id: Optional[int]

    # Product
    selected_product: Optional[Dict[str, Any]]

    # Specs
    human_spec_question_asked: bool      # tracks two-stage human_spec flow
    human_spec: Optional[Dict[str, Any]]
    technical_spec: Optional[Dict[str, Any]]

    # Pricing & Stock
    pricing_summary: Optional[Dict[str, Any]]
    stock_status: Optional[Dict[str, Any]]

    # Confirmation
    confirmation_status: bool
    confirmed_by_user: bool

    # Order
    order_id: Optional[int]
    receipt_path: Optional[str]

    # Supervisor
    supervisor_issue: Optional[str]
    supervisor_decision: Optional[Dict[str, Any]]


def get_initial_state(user_message: str) -> WoodWorksState:
    return WoodWorksState(
        mode="",
        current_node="intent_decider",
        supervisor_steps=0,
        error=None,
        workflow_complete=False,
        user_message=user_message,
        conversation_history=[],
        assistant_response="",
        refined_query=None,
        retrieved_context=None,
        reasoning_output=None,
        user_info=None,
        user_id=None,
        selected_product=None,
        human_spec_question_asked=False,
        human_spec=None,
        technical_spec=None,
        pricing_summary=None,
        stock_status=None,
        confirmation_status=False,
        confirmed_by_user=False,
        order_id=None,
        receipt_path=None,
        supervisor_issue=None,
        supervisor_decision=None,
    )
