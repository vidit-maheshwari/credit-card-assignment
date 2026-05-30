# Credit Card Spend Analytics — Frontend

React + Vite single-page application for visualizing credit card spending data.

## Tech Stack

- **React 19** with Vite
- **Recharts** for charts and graphs
- **Axios** for API communication
- **Lucide React** for icons
- **React Markdown** for chat message rendering

## Getting Started

```bash
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` by default.

## Project Structure

```
src/
├── api/
│   └── index.js          # API client (axios) — all backend calls
├── components/
│   ├── Dashboard.jsx     # Overview: monthly summary, top categories, charts
│   ├── Transactions.jsx  # Transaction list with filters (bank, category, month)
│   ├── Trends.jsx        # Spending trends over time (line/bar charts)
│   ├── Chat.jsx          # AI chat agent for natural language queries
│   └── Statements.jsx    # Upload PDFs, manage passwords, view imported statements
├── App.jsx               # Root component with tab navigation
├── App.css               # Global styles (dark neutral theme)
├── main.jsx              # Entry point
└── index.css             # Base CSS reset
```

## Features

| Tab | Description |
|-----|-------------|
| **Dashboard** | Monthly spending summary, category breakdown pie chart, top merchants |
| **Transactions** | Filterable table of all transactions with reward points |
| **Trends** | Month-over-month spending trends, category comparisons |
| **Ask Agent** | Chat with an AI agent about your spending data |
| **Statements** | Upload PDF statements, configure unlock password, manage imports |

## API Backend

The frontend expects the FastAPI backend running at `http://localhost:8009/api`. Configure in `src/api/index.js`.

## Build

```bash
npm run build
```

Output goes to `dist/`.
