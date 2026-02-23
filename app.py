import os
import sys
import streamlit as st

# ── Bootstrap path ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Logging setup (must happen before any other imports) ─────────────────────
from config.logging_config import setup_logging
logger = setup_logging()
logger.info("APP | WoodWorks AI starting up")

# ── Graph + State ─────────────────────────────────────────────────────────────
from graph.builder import get_graph
from graph.state import WoodWorksState, get_initial_state
from memory.short_term import get_state_summary, clear_workflow_state
from tools.db_tools import get_available_products

# ── Streamlit page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="WoodWorks AI",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #3B2314;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #7B5C3E;
        margin-top: 0;
    }
    .mode-badge-chat {
        background: #E8F4FD;
        color: #1a6fa8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .mode-badge-workflow {
        background: #FDF3E8;
        color: #a85c1a;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .step-complete { color: #2e7d32; }
    .step-pending  { color: #b0b0b0; }
    .step-active   { color: #a85c1a; font-weight: 600; }
    div[data-testid="stChatMessage"] { border-radius: 12px; }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
def _init_session():
    if "graph_state" not in st.session_state:
        st.session_state.graph_state = {}
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "waiting_for_confirmation" not in st.session_state:
        st.session_state.waiting_for_confirmation = False
    if "waiting_for_input" not in st.session_state:
        st.session_state.waiting_for_input = True
    if "order_complete" not in st.session_state:
        st.session_state.order_complete = False
    if "receipt_path" not in st.session_state:
        st.session_state.receipt_path = None
    if "confirmation_processing" not in st.session_state:
        st.session_state.confirmation_processing = False
    if "image_analysis_result" not in st.session_state:
        st.session_state.image_analysis_result = None
    if "image_processed" not in st.session_state:
        st.session_state.image_processed = False


_init_session()


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🪵 WoodWorks AI")
        st.markdown("*Enterprise Furniture Assistant*")
        st.divider()

        # Mode badge
        mode = st.session_state.graph_state.get("mode", "")
        if mode == "chat":
            st.markdown('<span class="mode-badge-chat">💬 Chat Mode</span>', unsafe_allow_html=True)
        elif mode == "workflow":
            st.markdown('<span class="mode-badge-workflow">⚙️ Workflow Mode</span>', unsafe_allow_html=True)
        else:
            st.markdown("*Mode: Detecting...*")

        st.divider()

        # Workflow progress
        if mode == "workflow":
            st.markdown("**Order Progress**")
            state = st.session_state.graph_state
            steps = [
                ("👤 User Info", bool(state.get("user_info"))),
                ("🪑 Product Selected", bool(state.get("selected_product"))),
                ("📝 Specifications", bool(state.get("human_spec"))),
                ("🔧 Technical Spec", bool(state.get("technical_spec"))),
                ("💰 Pricing", bool(state.get("pricing_summary"))),
                ("✅ Confirmed", bool(state.get("confirmed_by_user"))),
                ("📦 Order Created", bool(state.get("order_id"))),
                ("🧾 Receipt", bool(state.get("receipt_path"))),
            ]
            for label, done in steps:
                if done:
                    st.markdown(f'<span class="step-complete">✔ {label}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="step-pending">○ {label}</span>', unsafe_allow_html=True)

        # User summary
        user_info = st.session_state.graph_state.get("user_info")
        if user_info:
            st.divider()
            st.markdown("**Customer**")
            st.markdown(f"👤 {user_info.get('name', 'N/A')}")
            if user_info.get("email"):
                st.markdown(f"📧 {user_info['email']}")
            if user_info.get("phone"):
                st.markdown(f"📞 {user_info['phone']}")

        st.divider()

        # Quick product catalog
        st.markdown("**Our Catalog**")
        try:
            products = get_available_products()
            categories = sorted(set(p["category"] for p in products))
            for cat in categories:
                cat_products = [p for p in products if p["category"] == cat]
                with st.expander(f"📁 {cat} ({len(cat_products)})"):
                    for p in cat_products:
                        st.markdown(f"• **{p['name']}** — ${p['base_price']:,.0f}")
        except Exception:
            st.info("Loading catalog...")

        st.divider()
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ── Graph runner ──────────────────────────────────────────────────────────────
def run_graph(user_message: str) -> str:
    graph = get_graph()
    current_state = dict(st.session_state.graph_state)

    history = list(current_state.get("conversation_history") or [])
    history.append({"role": "user", "content": user_message})
    current_state["conversation_history"] = history

    # Inject new user message and reset per-turn fields
    current_state["user_message"] = user_message
    current_state["supervisor_issue"] = None
    current_state.setdefault("supervisor_steps", 0)

    logger.info(f"APP | run_graph | message='{user_message[:60]}...' node={current_state.get('current_node')}")

    try:
        result = graph.invoke(current_state)
        st.session_state.graph_state = dict(result)
        response = result.get("assistant_response", "").strip()

        if not response:
            current = result.get("current_node", "")
            if current == "technical_spec_agent":
                response = "Technical spec ready. Calculating stock and pricing now..."
            elif current == "stock_pricing_agent":
                response = "Pricing complete. Review your order summary above."
            else:
                response = "Processing your request, please continue..."

        # Check if waiting for confirmation
        if result.get("confirmation_status") and not result.get("confirmed_by_user"):
            st.session_state.waiting_for_confirmation = True

        # Check if receipt is ready
        if result.get("receipt_path"):
            st.session_state.receipt_path = result.get("receipt_path")

        if result.get("workflow_complete"):
            st.session_state.order_complete = True

        return response
    except Exception as e:
        logger.error(f"APP | run_graph | ERROR: {e}")
        return f"⚠️ An error occurred: {str(e)}. Please try again."


# ── Confirmation handler ──────────────────────────────────────────────────────
def handle_confirmation():
    # Guard against double-fire from Streamlit reruns
    if st.session_state.get("confirmation_processing"):
        logger.warning("APP | handle_confirmation | duplicate call blocked")
        return

    st.session_state.confirmation_processing = True

    st.session_state.waiting_for_confirmation = False

    st.session_state.graph_state["confirmed_by_user"] = True
    st.session_state.graph_state["confirmation_status"] = True
    st.session_state.graph_state["supervisor_issue"] = None
    st.session_state.graph_state["user_message"] = "CONFIRMED"

    state = dict(st.session_state.graph_state)

    logger.info(
        f"APP | handle_confirmation | invoking graph with "
        f"confirmed_by_user={state.get('confirmed_by_user')} "
        f"order_id={state.get('order_id')} "
        f"receipt_path={state.get('receipt_path')}"
    )

    graph = get_graph()
    try:
        result = graph.invoke(state)
        st.session_state.graph_state = dict(result)

        response = result.get("assistant_response", "").strip()
        if not response:
            response = "Processing your order... please wait a moment."

        if result.get("receipt_path"):
            st.session_state.receipt_path = result.get("receipt_path")

        st.session_state.order_complete = result.get("workflow_complete", False)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    except Exception as e:
        logger.error(f"APP | handle_confirmation | ERROR: {e}")
        st.error(f"Error confirming order: {e}")
        st.session_state.waiting_for_confirmation = True
    finally:
        st.session_state.confirmation_processing = False


# ── Main UI ───────────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    # Header
    st.markdown('<p class="main-header">🪵 WoodWorks AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enterprise Furniture Assistant — Powered by Groq & LangGraph</p>', unsafe_allow_html=True)
    st.divider()

    # Welcome message
    if not st.session_state.chat_messages:
        with st.chat_message("assistant"):
            st.markdown(
                "👋 Welcome to **WoodWorks AI**! I'm your enterprise furniture consultant.\n\n"
                "I can help you:\n"
                "- 💬 **Chat** — Ask about our products, materials, and craftsmanship\n"
                "- 🛒 **Order** — Say *'I'd like to place an order'* to start a custom furniture workflow\n\n"
                "How can I assist you today?"
            )

    # Chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if (st.session_state.waiting_for_confirmation
            and not st.session_state.get("confirmation_processing")
            and not st.session_state.graph_state.get("confirmed_by_user")):
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Confirm Order", type="primary", use_container_width=True,
                         key="confirm_order_btn"):
                handle_confirmation()
                st.rerun()
        with col2:
            if st.button("❌ Cancel Order", use_container_width=True):
                st.session_state.waiting_for_confirmation = False
                cancel_msg = "Order cancelled. Feel free to start a new order or ask me anything!"
                st.session_state.chat_messages.append({"role": "assistant", "content": cancel_msg})
                # Reset workflow state
                state = dict(st.session_state.graph_state)
                st.session_state.graph_state = clear_workflow_state(state)
                st.rerun()

    # Receipt download
    if st.session_state.receipt_path and os.path.exists(st.session_state.receipt_path):
        st.divider()
        with open(st.session_state.receipt_path, "rb") as f:
            order_id = st.session_state.graph_state.get("order_id", "")
            st.download_button(
                label=f"📥 Download Receipt — Order #{order_id}",
                data=f,
                file_name=os.path.basename(st.session_state.receipt_path),
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )

    # ── Image Upload (Optional) ────────────────────────────────────────────
    if not st.session_state.order_complete:
        with st.expander("📷 Upload a furniture image (optional)", expanded=False):
            uploaded_file = st.file_uploader(
                "Upload a photo of furniture you like or want to reference for your order",
                type=["jpg", "jpeg", "png", "webp"],
                key="furniture_image_upload",
            )

            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded image", width=200)

                # Auto-analyze on upload — no button click needed
                file_key = f"analyzed_{uploaded_file.name}_{uploaded_file.size}"
                if not st.session_state.get(file_key):
                    with st.spinner("Analyzing image..."):
                        image_bytes = uploaded_file.read()
                        media_type = uploaded_file.type  # already a MIME string

                        current_mode = st.session_state.graph_state.get(
                            "mode", "")

                        if current_mode == "workflow":
                            from tools.image_search import process_image_for_workflow
                            result = process_image_for_workflow(
                                image_bytes, media_type)

                            if result["success"]:
                                st.session_state.image_analysis_result = result
                                st.session_state.graph_state[
                                    "image_spec_hint"] = result["human_spec_hint"]
                                st.session_state[file_key] = True
                                msg = result["workflow_message"]
                                st.session_state.chat_messages.append(
                                    {"role": "assistant", "content": msg})
                                st.success("Image analyzed — specs pre-filled!")
                            else:
                                st.error(f"Could not analyze image: "
                                         f"{result.get('error')}")
                        else:
                            from tools.image_search import process_image_for_chat
                            result = process_image_for_chat(
                                image_bytes, media_type)

                            if result["success"]:
                                st.session_state.image_analysis_result = result
                                analysis_message = result["chat_response"]

                                # Append to UI messages
                                st.session_state.chat_messages.append(
                                    {"role": "assistant", "content": analysis_message})

                                # Sync to LangGraph conversation_history so chat agent sees it
                                history = list(
                                    st.session_state.graph_state.get(
                                        "conversation_history") or [])
                                history.append(
                                    {"role": "assistant", "content": analysis_message})
                                st.session_state.graph_state[
                                    "conversation_history"] = history

                                # Store structured hint for reasoning/response nodes
                                st.session_state.graph_state[
                                    "image_spec_hint"] = result["analysis"]

                                st.session_state[file_key] = True
                                st.rerun()
                            else:
                                st.error(f"Could not analyze image: "
                                         f"{result.get('error')}")

    # Chat input
    if not st.session_state.order_complete:
        user_input = st.chat_input("Type your message here...")
        if user_input:
            # Add user message to history
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Handle cancel
            if user_input.strip().lower() in ["cancel", "cancel order", "stop"]:
                state = dict(st.session_state.graph_state)
                st.session_state.graph_state = clear_workflow_state(state)
                st.session_state.waiting_for_confirmation = False
                response = "Order cancelled. Feel free to start fresh or ask me anything!"
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = run_graph(user_input)
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})

            st.rerun()
    else:
        st.success("🎉 Order complete! Thank you for choosing WoodWorks AI.")
        if st.button("🆕 Start New Order", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
