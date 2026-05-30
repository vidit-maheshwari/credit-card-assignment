import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import statements, transactions, analytics, chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Credit Card Spend Analytics",
    description="Local agentic tool for credit card spend analytics",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(statements.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(chat.router)


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized, application started")


@app.get("/")
def root():
    return {"message": "Credit Card Spend Analytics API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
