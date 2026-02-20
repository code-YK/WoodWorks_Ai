# 🪵 WoodWorks AI — Enterprise Furniture Assistant

A production-grade AI automation system built with LangGraph, Groq, SQLAlchemy, and Streamlit.

---

## 🏗️ Architecture

```
WoodWorks AI
├── Dual-Mode Graph (LangGraph)
│   ├── Chat Mode — Session-aware conversational assistant
│   └── Workflow Mode — Supervised order automation pipeline
├── LLM — Groq API (llama3-70b-8192)
├── Database — SQLAlchemy ORM (SQLite / PostgreSQL)
├── PDF Receipts — ReportLab
└── UI — Streamlit
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run the application

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
woodworks_ai/
├── app.py                        # Streamlit UI entry point
├── config/
│   ├── settings.py               # Centralized configuration
│   └── logging_config.py         # Structured logging setup
├── llm/
│   └── groq_client.py            # Groq API client (centralized)
├── graph/
│   ├── builder.py                # LangGraph graph construction
│   ├── state.py                  # WoodWorksState TypedDict
│   ├── routing.py                # Routing helper functions
│   └── nodes/
│       ├── final_confirmation.py # Hard gate before order creation
│       ├── create_order.py       # Order DB creation node
│       ├── generate_receipt.py   # PDF receipt generation node
│       └── store_memory.py       # Long-term memory persistence
├── agents/
│   ├── prompt_loader.py          # Centralized prompt file loader
│   ├── intent_decider.py         # Chat vs Workflow router
│   ├── chat_agent.py             # Session-aware chat agent
│   ├── user_info.py              # User information collector
│   ├── product_selector.py       # Product selection agent
│   ├── human_spec.py             # 2-stage spec collection agent
│   ├── technical_spec.py         # Engineering spec generator
│   ├── pricing.py                # Stock check + price calculator
│   └── supervisor.py             # LLM-based ambiguity resolver
├── tools/
│   ├── db_tools.py               # All database tool functions
│   ├── order_tools.py            # Order creation tools
│   └── pdf_generator.py          # ReportLab PDF receipt generator
├── database/
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── session.py                # Session management + context manager
│   └── seed_data.py              # 22 product catalog seeds
├── memory/
│   ├── short_term.py             # LangGraph state utilities
│   └── long_term.py              # workflow_memory DB queries
├── prompts/                      # All LLM prompts (one file per agent)
│   ├── intent_decider.txt
│   ├── chat.txt
│   ├── user_info.txt
│   ├── product_selector.txt
│   ├── human_spec_questions.txt
│   ├── human_spec_extraction.txt
│   ├── technical_spec.txt
│   ├── pricing.txt
│   └── supervisor.txt
├── schemas/
│   └── state_schema.py           # Pydantic validation schemas
├── receipts/                     # Generated PDF receipts
└── logs/                         # Structured log files
```

---

## 🔄 Workflow Flow

```
User Message
    ↓
Intent Decider (LLM) ---------------
    ↓                               ↓
[Chat Mode]                    [Workflow Mode]
    ↓                               ↓
Chat Agent                   User Info Collector
(session memory)                    ↓
                             Product Selector
                                    ↓
                             Human Spec Agent
                             (LLM questions → extraction)
                                    ↓
                             Technical Spec Agent
                             (LLM translation)
                                    ↓
                             Stock & Pricing Agent
                                    ↓
                          ↙ Insufficient Stock?
              Supervisor (LLM)
                            ↓ 
              Suggests alternative
                            ↓
                     Final Confirmation (Hard Gate)
                            ↓ User clicks Confirm
                     Create Order (DB)
                            ↓
                     Generate PDF Receipt
                            ↓
                     Store Long-Term Memory
                            ↓
                     END
```

---

## 🧠 Memory Architecture

| Layer | Storage | Lifecycle |
|-------|---------|-----------|
| Short-term | LangGraph State | Per session, cleared on reset |
| Long-term | `workflow_memory` DB table | Persistent across sessions |

---

## 📊 Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Customer records |
| `product_catalog` | 22 seeded furniture products |
| `product_items` | Inventory with SKUs |
| `orders` | Confirmed orders |
| `workflow_memory` | Long-term agent memory |

---

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key | ✅ Yes |
| `DATABASE_URL` | SQLAlchemy DB URL | Optional (defaults to SQLite) |
| `LOG_LEVEL` | Logging level | Optional (defaults to INFO) |

---

## 📝 Logging

All logs are written to:
- **Console** — Real-time structured output
- **`logs/app.log`** — Persistent file log

Log format: `TIMESTAMP | LEVEL | MODULE | MESSAGE`

---

## 🧾 PDF Receipts

Generated receipts are stored in `receipts/receipt_<order_id>.pdf` and include:
- Company name and branding
- Order ID, date, customer name
- Product and customization details
- Technical specification summary
- Final price

---

## ⚙️ Configuration

Edit `config/settings.py` to change:
- `GROQ_MODEL` — LLM model (default: `llama3-70b-8192`)
- `MAX_SUPERVISOR_STEPS` — Supervisor loop guard (default: 10)
- `COMPANY_NAME` — Appears in UI and PDF receipts
