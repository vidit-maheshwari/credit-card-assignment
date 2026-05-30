"""
Agentic chat service using Groq LLM.
The LLM is used ONLY for intent parsing and response generation.
All numerical calculations are done deterministically by the analytics service.
"""

import json
from typing import Optional
from groq import Groq
from sqlalchemy.orm import Session
from app.config import settings
from app.services.analytics import (
    get_monthly_analytics,
    get_multi_month_trends,
    get_available_months,
    get_transactions,
)

SYSTEM_PROMPT = """You are a Credit Card Spend Analytics assistant. You help users understand their credit card spending patterns, rewards, and trends.

You have access to the following tools to answer user questions. ALWAYS use these tools for data - never make up numbers.

Available tools:
1. get_monthly_analytics(month: str, bank?: str) - Get spending analytics for a specific month (format: YYYY-MM)
2. get_trends(months: list[str], bank?: str) - Get multi-month spending trends
3. get_transactions(month?: str, category?: str, bank?: str, limit?: int) - Get individual transactions
4. get_available_months() - Get list of months with data

IMPORTANT - Categories available in the system:
Dining, Travel, Groceries, Fuel, Utilities, Shopping, Entertainment, Rent, Healthcare, Education, Insurance, EMI, Payment, Other

When the user asks about "food", use category "Dining".
When the user asks about "bills", use category "Utilities".
When the user asks about "movies" or "shows", use category "Entertainment".
When the user asks about "medical", use category "Healthcare".

When responding:
- Always call a tool to get real data before answering
- Present numbers clearly and formatted
- If the user's request is ambiguous, ask for clarification
- Never fabricate financial data
- If no month is specified, omit the month param to get data across all months

Respond with a JSON object with these fields:
- "tool": the tool name to call (or "none" if just conversational)
- "params": parameters for the tool as a JSON object
- "message": your response text to show to the user (fill this after seeing tool results)

For the first response, just provide the tool call. I'll give you the results, then you provide the final message.
"""


def get_groq_client() -> Optional[Groq]:
    """Initialize Groq client."""
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        return None
    return Groq(api_key=settings.GROQ_API_KEY)


def process_chat(db: Session, user_message: str) -> dict:
    """
    Process a chat message using the agentic flow:
    1. LLM parses intent and decides which tool to call
    2. Tool executes deterministically
    3. LLM formats the response for the user
    """
    client = get_groq_client()

    if not client:
        return _fallback_response(db, user_message)

    try:
        # Step 1: Get tool call from LLM
        tool_response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
            max_tokens=500,
        )

        tool_call_text = tool_response.choices[0].message.content.strip()

        # Parse the tool call
        tool_call = _parse_tool_call(tool_call_text)

        if not tool_call or tool_call.get("tool") == "none":
            return {"response": tool_call.get("message", "I can help you with credit card spend analytics. Try asking about your spending for a specific month!"), "data": None}

        # Step 2: Execute the tool deterministically
        tool_result = _execute_tool(db, tool_call["tool"], tool_call.get("params", {}))

        # Step 3: Get formatted response from LLM
        format_response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a Credit Card Spend Analytics assistant. Format the following data into a clear, readable response for the user. Use bullet points and proper formatting. All numbers should be presented as-is (do not recalculate). Use ₹ for currency amounts."},
                {"role": "user", "content": f"User asked: {user_message}\n\nHere is the data:\n{json.dumps(tool_result, indent=2, default=str)}"},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        formatted = format_response.choices[0].message.content.strip()
        return {"response": formatted, "data": tool_result}

    except Exception as e:
        return _fallback_response(db, user_message)


def _parse_tool_call(text: str) -> Optional[dict]:
    """Parse the LLM's tool call response."""
    try:
        # Try to extract JSON from the response
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
    return None


def _execute_tool(db: Session, tool_name: str, params: dict) -> dict:
    """Execute a tool deterministically."""
    if tool_name == "get_monthly_analytics":
        month = params.get("month", "")
        if not month:
            months = get_available_months(db)
            month = months[-1] if months else ""
        bank = params.get("bank")
        return get_monthly_analytics(db, month, bank)

    elif tool_name == "get_trends":
        months = params.get("months", [])
        if not months:
            months = get_available_months(db)
        bank = params.get("bank")
        return get_multi_month_trends(db, months, bank)

    elif tool_name == "get_transactions":
        result = get_transactions(
            db,
            month=params.get("month"),
            category=params.get("category"),
            bank=params.get("bank"),
            limit=params.get("limit", 20),
        )
        # Convert ORM objects to dicts for JSON serialization
        result["transactions"] = [
            {
                "transaction_date": str(t.transaction_date),
                "merchant_description": t.merchant_description,
                "amount": t.amount,
                "transaction_type": t.transaction_type,
                "category": t.category,
                "reward_points": t.reward_points,
            }
            for t in result["transactions"]
        ]
        return result

    elif tool_name == "get_available_months":
        return {"months": get_available_months(db)}

    else:
        return {"error": f"Unknown tool: {tool_name}"}


def _fallback_response(db: Session, user_message: str) -> dict:
    """Provide a basic response without LLM when API key is not configured."""
    message_lower = user_message.lower()

    available_months = get_available_months(db)

    if not available_months:
        return {
            "response": "No statement data found. Please place your credit card statement PDFs/CSVs in the statements_inbox folder and click 'Ingest Statements'.",
            "data": None,
        }

    # Simple keyword-based intent detection
    if any(word in message_lower for word in ["trend", "month over month", "compare", "last few months"]):
        data = get_multi_month_trends(db, available_months[-6:])
        return {
            "response": f"Here are your spending trends for {', '.join(available_months[-6:])}. Total spend trend: {data['total_spend_trend']}. Check the trends chart for visual details.",
            "data": data,
        }

    # Try to extract a month
    target_month = None
    for month in available_months:
        if month in message_lower:
            target_month = month
            break

    if not target_month and available_months:
        target_month = available_months[-1]

    data = get_monthly_analytics(db, target_month)
    response = (
        f"For {target_month}:\n"
        f"• Total spend: ₹{data['total_spend']:,.2f}\n"
        f"• Total rewards: {data['total_rewards']:,.0f} points\n"
        f"• Top spending category: {max(data['category_spend'], key=data['category_spend'].get) if data['category_spend'] else 'N/A'}\n"
        f"• Best reward category: {data['highest_reward_category'] or 'N/A'}\n"
        f"\nConfigure your GROQ_API_KEY in .env for natural language queries."
    )

    return {"response": response, "data": data}
