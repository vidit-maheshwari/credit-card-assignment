"""
LLM-based PDF statement parser.
Extracts text from PDF using pdfplumber, then uses Groq LLM to parse
transactions into structured data matching the database model.
"""

import json
import logging
from datetime import date
from typing import Optional
import pdfplumber
from groq import Groq
from app.config import settings
from app.services.reward_calculator import calculate_reward_points

logger = logging.getLogger(__name__)


PARSE_PROMPT = """You are a credit card statement parser. Extract ALL transactions from the following credit card statement text.

Return a JSON object with this exact structure:
{
  "bank": "bank name (e.g., HDFC, ICICI, SBI, Axis, etc.)",
  "card_type": "card type if mentioned (e.g., Freedom Credit Card, Platinum, etc.)",
  "statement_month": "YYYY-MM format of the statement billing period end month",
  "total_reward_points_earned": 0,
  "transactions": [
    {
      "transaction_date": "YYYY-MM-DD",
      "merchant_description": "merchant/payee name and location",
      "amount": 123.45,
      "transaction_type": "debit or credit",
      "reward_points": 0.0,
      "category": "category like Dining, Shopping, Travel, Groceries, Fuel, Utilities, Entertainment, Rent, Healthcare, Education, Insurance, EMI, Payment, or Other"
    }
  ]
}

Rules:
- Extract EVERY transaction listed in the statement
- For merchant_description, provide a clean readable name (separate city name if merged with text)
- transaction_type: "debit" for purchases/charges, "credit" for payments/refunds
- Determine category from the merchant description
- REWARD POINTS: Look for a "Reward Points" balance section showing "Earned" points for this billing cycle.
  - total_reward_points_earned: set this to the "Earned" value (e.g., if row shows "Opening: 0, Earned: 40, Disbursed: 0", set to 40)
  - For individual transaction reward_points: just set to 0 (the system will distribute automatically based on the total)
- statement_month should be the end month of the billing period in YYYY-MM format
- Amounts should be positive numbers regardless of debit/credit
- Return ONLY the JSON object, no other text

Statement text:
"""


def extract_text_from_pdf(filepath: str, password: str = None) -> str:
    """Extract all text from a PDF file."""
    open_kwargs = {}
    if password:
        open_kwargs["password"] = password

    logger.info(f"Opening PDF with password={'yes' if password else 'no'}")
    text = ""
    try:
        with pdfplumber.open(filepath, **open_kwargs) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        logger.error(f"PDF open/read error: {type(e).__name__}: {repr(e)}")
        raise

    logger.info(f"Extracted {len(text.strip())} chars from PDF")
    return text


def parse_statement_with_llm(filepath: str, password: str = None) -> dict:
    """
    Parse a credit card statement PDF using LLM.
    Returns structured data: {bank, card_type, statement_month, transactions: [...]}
    """
    # Step 1: Extract text from PDF
    logger.info(f"Extracting text from: {filepath}")
    text = extract_text_from_pdf(filepath, password)

    if not text.strip():
        raise ValueError("Could not extract any text from the PDF. The file may be corrupted or empty.")

    logger.info(f"Extracted {len(text)} chars, sending to LLM ({settings.GROQ_MODEL})")

    # Step 2: Send to LLM for parsing
    client = Groq(api_key=settings.GROQ_API_KEY)

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a precise financial document parser. Return only valid JSON."
            },
            {
                "role": "user",
                "content": PARSE_PROMPT + text
            }
        ],
        temperature=0,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )

    result_text = response.choices[0].message.content
    logger.debug(f"LLM response length: {len(result_text)} chars")

    # Step 3: Parse LLM response
    try:
        parsed = json.loads(result_text)
    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON: {result_text[:200]}")
        raise ValueError(f"LLM returned invalid JSON: {e}")

    # Validate required fields
    if "transactions" not in parsed:
        raise ValueError("LLM response missing 'transactions' field")

    # Ensure defaults
    parsed.setdefault("bank", "Unknown")
    parsed.setdefault("card_type", "Credit Card")
    parsed.setdefault("statement_month", "Unknown")

    # Calculate reward points using bank/card-specific rules
    total_pts = parsed.get("total_reward_points_earned", 0) or 0
    if total_pts > 0:
        parsed["transactions"] = calculate_reward_points(
            parsed["transactions"],
            bank=parsed["bank"],
            card_type=parsed["card_type"],
            total_earned=total_pts,
        )

    logger.info(f"Parsed: bank={parsed['bank']}, month={parsed['statement_month']}, txns={len(parsed['transactions'])}, reward_pts={total_pts}")

    return parsed
