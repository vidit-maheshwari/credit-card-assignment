# Credit Card Spend Analytics — Backend

FastAPI backend that ingests credit card PDF statements, parses them with an LLM, and provides analytics APIs.

## Tech Stack

- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM with SQLite
- **pdfplumber** — PDF text extraction
- **Groq** (llama-3.3-70b-versatile) — LLM-based statement parsing
- **Uvicorn** — ASGI server

## Getting Started

```bash
python -m venv venv
.\venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`):

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Run the server:

```bash
uvicorn main:app --reload --port 8009
```

API docs at `http://localhost:8009/docs`.

## Project Structure

```
backend/
├── main.py                     # FastAPI app entry point, CORS, router registration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys)
├── spend_analytics.db          # SQLite database (auto-created)
├── statements_inbox/           # Drop PDF statements here for folder-based ingestion
└── app/
    ├── config.py               # Settings (paths, API keys, model config)
    ├── database.py             # SQLAlchemy engine & session setup
    ├── models/
    │   ├── schema.py           # ORM models: Statement, Transaction, UserConfig
    │   └── dto.py              # Pydantic request/response schemas
    ├── routers/
    │   ├── statements.py       # /api/statements — upload, ingest, delete, password mgmt
    │   ├── transactions.py     # /api/transactions — list/filter transactions
    │   ├── analytics.py        # /api/analytics — monthly summaries, category breakdowns
    │   └── chat.py             # /api/chat — AI agent for natural language queries
    └── services/
        ├── llm_parser.py       # PDF text extraction + Groq LLM parsing
        ├── reward_calculator.py# Bank/card-specific reward point calculation
        ├── ingestion.py        # File processing, deduplication, DB storage
        ├── analytics.py        # Analytics queries (monthly, categories, trends)
        ├── chat.py             # Chat agent with tool-calling (Groq)
        └── categorizer.py      # Transaction category utilities
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/statements/upload` | Upload a PDF statement |
| POST | `/api/statements/ingest` | Ingest all PDFs from `statements_inbox/` |
| GET | `/api/statements/` | List all imported statements |
| DELETE | `/api/statements/{id}` | Delete a statement and its transactions |
| POST | `/api/statements/password` | Save PDF unlock password |
| GET | `/api/statements/password` | Get saved password |
| GET | `/api/transactions/` | List transactions (filterable by bank, category, month) |
| GET | `/api/analytics/months` | Get available statement months |
| GET | `/api/analytics/monthly` | Monthly spending summary |
| GET | `/api/analytics/categories` | Category breakdown |
| GET | `/api/analytics/trends` | Spending trends over time |
| POST | `/api/chat/` | Chat with the AI analytics agent |

## Reward Points

Reward points are calculated using bank/card-specific rules defined in `app/services/reward_calculator.py`. Currently configured:

- **HDFC Freedom Credit Card**: 1 CashPoint per ₹150 on all spends (excluding fuel, EMI, payments)

The calculator extracts the total earned points from the statement, then distributes them across eligible transactions proportionally using the card's rate formula.

## Database

SQLite with three tables:
- `statements` — imported statement metadata (bank, month, filename, hash)
- `transactions` — individual transactions (date, merchant, amount, category, reward points)
- `user_config` — key-value settings (PDF password)
