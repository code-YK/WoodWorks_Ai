import logging
from langgraph.graph import StateGraph, END
from graph.state import WoodWorksState

# Agents & Nodes
from agents.intent_decider import intent_decider_node
from agents.user_info import user_info_collector_node
from agents.product_selector import product_selector_node
from agents.human_spec import human_spec_agent_node
from agents.technical_spec import technical_spec_agent_node
from agents.pricing import stock_pricing_agent_node
from agents.supervisor import supervisor_node

# Chat Subgraph Nodes
from agents.chat_subgraph.query_refinement import query_refinement_node
from agents.chat_subgraph.data_retrieval import data_retrieval_node
from agents.chat_subgraph.reasoning import reasoning_node
from agents.chat_subgraph.response_generator import response_generator_node
from agents.chat_subgraph.store_chat_summary import store_chat_summary_node

# Workflow Subgraph Nodes
from graph.nodes.final_confirmation import final_confirmation_node
from graph.nodes.create_order import create_order_node
from graph.nodes.generate_receipt import generate_receipt_node
from graph.nodes.store_memory import store_memory_node

logger = logging.getLogger(__name__)


def _route_after_intent(state: WoodWorksState) -> str:
    # Route to either Chat Subgraph or Workflow Dispatcher
    return "workflow_dispatcher" if state.get("mode") == "workflow" else "query_refinement"


def _route_from_dispatcher(state: WoodWorksState) -> str:
    """Happy-path dispatcher: deterministically routes to the next incomplete step.
    The Supervisor is ONLY reachable when supervisor_issue is explicitly set.
    The dispatcher NEVER routes to END — store_memory is always the terminal node."""

    confirmed  = state.get("confirmed_by_user")
    order_id   = state.get("order_id")
    receipt    = state.get("receipt_path")

    logger.info(
        f"DISPATCHER | confirmed={confirmed} order_id={order_id} receipt={receipt} "
        f"user_info={bool(state.get('user_info'))} product={bool(state.get('selected_product'))} "
        f"human_spec={bool(state.get('human_spec'))} tech_spec={bool(state.get('technical_spec'))} "
        f"pricing={bool(state.get('pricing_summary'))}"
    )

    # Only route to supervisor on a real, non-empty issue
    if state.get("supervisor_issue") and state["supervisor_issue"] != "":
        logger.info("DISPATCHER | routing → supervisor")
        return "supervisor"

    # Deterministic happy-path: find the first incomplete step
    if not state.get("user_info"):
        logger.info("DISPATCHER | routing → user_info_collector")
        return "user_info_collector"

    if not state.get("selected_product"):
        logger.info("DISPATCHER | routing → product_selector")
        return "product_selector"

    # BUG 2B FIX: empty dict {} is truthy — require raw_answers to be present
    human_spec = state.get("human_spec")
    if not human_spec or not isinstance(human_spec, dict) or not human_spec.get("raw_answers"):
        logger.info("DISPATCHER | routing → human_spec_agent")
        return "human_spec_agent"

    if not state.get("technical_spec"):
        logger.info("DISPATCHER | routing → technical_spec_agent")
        return "technical_spec_agent"

    if not state.get("pricing_summary") or not state.get("stock_status"):
        logger.info("DISPATCHER | routing → stock_pricing_agent")
        return "stock_pricing_agent"

    # BUG 1 + BUG 2 FIX: confirmed must be checked BEFORE order_id.
    # final_confirmation always leads to END in a single turn.
    # Only after the user clicks Confirm (confirmed=True) does a NEW invoke() reach here.
    if not confirmed:
        logger.info("DISPATCHER | routing → final_confirmation")
        return "final_confirmation"

    # Post-confirmation linear fulfillment chain
    if not order_id:
        logger.info("DISPATCHER | routing → create_order")
        return "create_order"

    if not receipt:
        logger.info("DISPATCHER | routing → generate_receipt")
        return "generate_receipt"

    # All steps complete — run store_memory as the terminal node (never END directly)
    logger.info("DISPATCHER | routing → store_memory")
    return "store_memory"


def build_graph() -> StateGraph:
    logger.info("GRAPH | Building WoodWorks LangGraph (Consolidated)")
    builder = StateGraph(WoodWorksState)

    # 1. Intent Decider
    builder.add_node("intent_decider", intent_decider_node)

    # 2. Chat Subgraph Nodes
    builder.add_node("query_refinement",   query_refinement_node)
    builder.add_node("data_retrieval",     data_retrieval_node)
    builder.add_node("reasoning",          reasoning_node)
    builder.add_node("response_generator", response_generator_node)
    builder.add_node("store_chat_summary", store_chat_summary_node)

    # 3. Workflow Nodes
    builder.add_node("workflow_dispatcher",  lambda state: state)  # passthrough router
    builder.add_node("supervisor",           supervisor_node)
    builder.add_node("user_info_collector",  user_info_collector_node)
    builder.add_node("product_selector",     product_selector_node)
    builder.add_node("human_spec_agent",     human_spec_agent_node)
    builder.add_node("technical_spec_agent", technical_spec_agent_node)
    builder.add_node("stock_pricing_agent",  stock_pricing_agent_node)

    # 4. Fulfillment Nodes
    builder.add_node("final_confirmation", final_confirmation_node)
    builder.add_node("create_order",       create_order_node)
    builder.add_node("generate_receipt",   generate_receipt_node)
    builder.add_node("store_memory",       store_memory_node)

    # ── Entry Point ───────────────────────────────────────────────────────────
    builder.set_entry_point("intent_decider")

    # ── Intent Routing ────────────────────────────────────────────────────────
    builder.add_conditional_edges(
        "intent_decider",
        _route_after_intent,
        {
            "query_refinement":   "query_refinement",
            "workflow_dispatcher": "workflow_dispatcher",
        },
    )

    # ── Workflow Dispatcher ───────────────────────────────────────────────────
    # BUG 2 FIX (Part C): All routing targets must be declared in this map.
    # Missing keys cause LangGraph to silently fall through to END.
    builder.add_conditional_edges(
        "workflow_dispatcher",
        _route_from_dispatcher,
        {
            "supervisor":           "supervisor",
            "user_info_collector":  "user_info_collector",
            "product_selector":     "product_selector",
            "human_spec_agent":     "human_spec_agent",
            "technical_spec_agent": "technical_spec_agent",
            "stock_pricing_agent":  "stock_pricing_agent",
            "final_confirmation":   "final_confirmation",
            "create_order":         "create_order",       # ← was missing
            "generate_receipt":     "generate_receipt",   # ← was missing
            "store_memory":         "store_memory",       # ← was missing
        },
    )

    # Supervisor → re-evaluate via dispatcher
    builder.add_edge("supervisor", "workflow_dispatcher")

    # ── Chat Subgraph (Linear) ────────────────────────────────────────────────
    builder.add_edge("query_refinement",   "data_retrieval")
    builder.add_edge("data_retrieval",     "reasoning")
    builder.add_edge("reasoning",          "response_generator")
    builder.add_edge("response_generator", "store_chat_summary")
    builder.add_edge("store_chat_summary", END)

    # ── Workflow Worker Spokes → END ──────────────────────────────────────────
    # Each worker responds to the user and ends the turn.
    # The next user message re-enters via intent_decider → dispatcher.
    for node in [
        "user_info_collector",
        "product_selector",
        "human_spec_agent",
        "technical_spec_agent",
        "stock_pricing_agent",
    ]:
        builder.add_edge(node, END)

    # ── BUG 1 FIX: final_confirmation → END (never continues to create_order) ─
    # The old edge was: final_confirmation → order_fulfillment (same turn = bug).
    # Now: final_confirmation ends the turn. Only a NEW invoke() with
    # confirmed_by_user=True will route past this node to create_order.
    builder.add_edge("final_confirmation", END)

    # ── BUG 2 FIX (Part D): Post-confirmation linear fulfillment chain ────────
    # Once create_order starts, the full chain runs in a single graph turn.
    builder.add_edge("create_order",     "generate_receipt")
    builder.add_edge("generate_receipt", "store_memory")
    builder.add_edge("store_memory",     END)

    logger.info("GRAPH | Graph built successfully")
    return builder.compile()


# Singleton graph
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


# Expose graph for LangGraph Studio
graph = build_graph()
