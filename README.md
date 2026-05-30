# Credit Card Spend Analytics Agent

A local agentic tool that ingests credit card PDF statements, extracts transaction and reward data using LLM-based parsing, and provides spend analytics with an AI-powered chat interface.

## Architecture

```
┌─────────────────┐       ┌──────────────────────────────────────┐
│   React + Vite  │◄─────►│         FastAPI Backend               │
│   Frontend      │  API  │                                      │
│   (Port 5174)   │       │  ┌──────────────────────────────┐   │
└────────────────┘       │  │  Groq LLM (llama-3.3-70b)    │   │
                          │  │  - PDF Statement Parsing      │   │
                          │  │  - Chat Agent (Intent/Tools)  │   │
                          │  └──────────────────────────────┘   │
                          │  ┌──────────────────────────────┐   │
                          │  │  Reward Calculator            │   │
                          │  │  (Bank/Card-specific rules)   │   │
                          │  └──────────────────────────────┘   │
                          │  ┌──────────────────────────────┐   │
                          │  │  Analytics Engine             │   │
                          │  │  (Deterministic Python)       │   │
                          │  └──────────────────────────────┘   │
                          │  ┌──────────────────────────────┐   │
                          │  │  SQLite Database              │   │
                          │  │  (Statements, Transactions)   │   │
                          │  └──────────────────────────────┘   │
                          └──────────────────────────────────────┘
```

## Supported Banks & Cards

Currently supported with full reward point calculation:

| Bank | Card | Reward Rate |
|------|------|-------------|
| **HDFC** | Freedom Credit Card | 1 CashPoint per ₹150 spent (excludes Fuel, EMI, Payments) |

> The LLM parser can extract transactions from any bank's PDF, but reward point rules are only configured for HDFC Freedom. To add another card, update `backend/app/services/reward_calculator.py`.

## Features

- **LLM-Based Parsing**: Groq LLM extracts transactions from any bank's PDF — no per-bank regex parsers needed
- **Auto Bank Detection**: Bank identified from PDF content (HDFC, ICICI, SBI, Axis)
- **Card-Specific Rewards**: Reward points calculated using configurable bank/card rules (HDFC Freedom: 1pt per ₹150)
- **Password-Protected PDFs**: Auto-generates unlock password from user details
- **Monthly Analytics**: Total spend, rewards, category breakdown
- **Multi-Month Trends**: Spend/reward trends, MoM changes, stacked charts
- **AI Chat Agent**: Ask natural language questions about your spending
- **Duplicate Detection**: SHA256 hash-based deduplication
- **Source Traceability**: Every number traces back to a specific transaction

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Run the backend:
```bash
uvicorn main:app --reload --port 8009
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5174

### Using the App

1. Open the UI → Statements tab
2. Configure your PDF password (first name + DOB)
3. Upload credit card statement PDFs
4. View analytics on the Dashboard, Transactions, and Trends tabs
5. Ask questions in the "Ask Agent" tab

## Demo

[![Watch the demo](https://img.youtube.com/vi/kqMsFS0oIB8/maxresdefault.jpg)](https://youtu.be/kqMsFS0oIB8)

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, pdfplumber, Groq SDK
- **Frontend**: React 19, Vite, Recharts, Axios, Lucide React
- **LLM**: Groq (LLama 3.3 70B Versatile)

