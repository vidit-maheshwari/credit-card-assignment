"""
Reward points calculator.
Bank and card-specific reward point calculation rules.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


# ─── Reward Rules Configuration ───────────────────────────────────────────────
# Each card config defines how reward points are earned per transaction.
# Structure: BANK -> CARD_TYPE -> rules

REWARD_RULES = {
    "HDFC": {
        "Freedom Credit Card": {
            # Points earned per rupee spent, by category
            # HDFC Freedom: 1 CashPoint per ₹150 on all spends except fuel
            "default_rate": 1 / 150,  # 1 point per ₹150
            "category_rates": {
                "groceries": 1 / 150,
                "dining": 1 / 150,
                "shopping": 1 / 150,
                "travel": 1 / 150,
                "entertainment": 1 / 150,
                "utilities": 1 / 150,
                "healthcare": 1 / 150,
                "education": 1 / 150,
                "other": 1 / 150,
            },
            # Categories that earn 0 points
            "excluded_categories": ["fuel", "payment", "emi"],
            # Minimum transaction amount to earn points (₹)
            "min_txn_amount": 0,
        },
    },
}


def calculate_reward_points(transactions: list, bank: str, card_type: str, total_earned: float) -> list:
    """
    Calculate reward points for each transaction based on bank/card rules.

    If total_earned is provided from the statement, we use the bank's rate formula
    to compute relative points per transaction, then scale to match the actual total.

    Args:
        transactions: list of transaction dicts from LLM parser
        bank: bank name (e.g., "HDFC")
        card_type: card type (e.g., "Freedom Credit Card")
        total_earned: total reward points earned as shown in the statement

    Returns:
        transactions list with reward_points populated
    """
    # Find matching rule config
    rules = _get_rules(bank, card_type)

    if not rules:
        # No specific rules found — fallback: distribute proportionally by amount
        logger.warning(f"No reward rules for {bank}/{card_type}, using proportional distribution")
        return _distribute_proportional(transactions, total_earned)

    excluded = [c.lower() for c in rules.get("excluded_categories", [])]
    default_rate = rules.get("default_rate", 0)
    category_rates = rules.get("category_rates", {})

    # Calculate raw points per transaction using the card's rate
    raw_points = []
    for txn in transactions:
        category = (txn.get("category") or "other").lower()
        txn_type = (txn.get("transaction_type") or "debit").lower()

        if txn_type == "credit" or category in excluded:
            raw_points.append(0.0)
            continue

        amount = float(txn.get("amount", 0))
        rate = category_rates.get(category, default_rate)
        raw_points.append(amount * rate)

    total_raw = sum(raw_points)

    # Scale raw points to match the actual total from the statement
    if total_earned > 0 and total_raw > 0:
        scale_factor = total_earned / total_raw
        for i, txn in enumerate(transactions):
            if raw_points[i] > 0:
                txn["reward_points"] = round(raw_points[i] * scale_factor, 2)
            else:
                txn["reward_points"] = 0.0
    elif total_earned > 0:
        # All rates are 0 but we have points — distribute proportionally
        return _distribute_proportional(transactions, total_earned)
    else:
        # No points earned
        for txn in transactions:
            txn["reward_points"] = 0.0

    return transactions


def _get_rules(bank: str, card_type: str) -> dict:
    """Look up reward rules for a bank/card combination."""
    bank_rules = REWARD_RULES.get(bank)
    if not bank_rules:
        # Try partial/case-insensitive match (e.g., "HDFC Bank" matches "HDFC")
        bank_lower = (bank or "").lower()
        for key, val in REWARD_RULES.items():
            if key.lower() in bank_lower or bank_lower in key.lower():
                bank_rules = val
                break
    if not bank_rules:
        return {}

    card_rules = bank_rules.get(card_type)
    if not card_rules:
        # Try partial/case-insensitive match
        card_lower = (card_type or "").lower()
        for key, val in bank_rules.items():
            if key.lower() in card_lower or card_lower in key.lower():
                return val
        # If only one card type defined, use it as default
        if len(bank_rules) == 1:
            return list(bank_rules.values())[0]
    return card_rules or {}


def _distribute_proportional(transactions: list, total_earned: float) -> list:
    """Fallback: distribute points proportionally by amount across eligible debits."""
    eligible = [
        (i, t) for i, t in enumerate(transactions)
        if t.get("transaction_type") == "debit"
        and (t.get("category") or "").lower() not in ("payment", "emi")
    ]

    total_amount = sum(t.get("amount", 0) for _, t in eligible)

    for txn in transactions:
        txn["reward_points"] = 0.0

    if total_amount > 0 and eligible:
        distributed = 0.0
        for idx, (i, t) in enumerate(eligible):
            if idx == len(eligible) - 1:
                transactions[i]["reward_points"] = round(total_earned - distributed, 2)
            else:
                share = round(total_earned * t["amount"] / total_amount, 2)
                transactions[i]["reward_points"] = share
                distributed += share

    return transactions
