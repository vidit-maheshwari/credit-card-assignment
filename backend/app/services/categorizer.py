"""
Rules-based category inference engine.
Maps merchant descriptions to categories using keyword matching.
"""

from typing import Optional

CATEGORY_RULES = {
    "Dining": [
        "restaurant", "cafe", "coffee", "zomato", "swiggy", "dominos", "pizza",
        "burger", "mcdonalds", "kfc", "subway", "starbucks", "food", "biryani",
        "diner", "eatery", "bakery", "ice cream", "dessert", "chai", "tea",
        "bar", "pub", "brewery", "kitchen", "dhaba", "canteen", "meal",
        "uber eats", "dunzo", "blinkit food"
    ],
    "Travel": [
        "airline", "flight", "makemytrip", "goibibo", "irctc", "railway",
        "hotel", "oyo", "airbnb", "booking.com", "cleartrip", "yatra",
        "indigo", "spicejet", "air india", "vistara", "airport", "cab",
        "uber", "ola", "rapido", "train", "bus", "redbus", "travel",
        "tourism", "tour", "trip"
    ],
    "Groceries": [
        "grocery", "bigbasket", "blinkit", "zepto", "dmart", "reliance fresh",
        "more", "supermarket", "provision", "kirana", "vegetables", "fruits",
        "jiomart", "amazon fresh", "nature basket", "grofers", "instamart",
        "swiggy instamart"
    ],
    "Fuel": [
        "petrol", "diesel", "fuel", "hp petroleum", "indian oil", "bharat petroleum",
        "iocl", "bpcl", "hpcl", "gas station", "filling station", "cng",
        "shell", "nayara"
    ],
    "Utilities": [
        "electricity", "water", "gas bill", "internet", "broadband", "wifi",
        "jio", "airtel", "vodafone", "vi ", "bsnl", "phone bill", "mobile recharge",
        "dth", "tata sky", "dish tv", "postpaid", "prepaid", "utility",
        "municipal", "maintenance"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "nykaa", "meesho",
        "snapdeal", "shoppers stop", "lifestyle", "westside", "h&m",
        "zara", "clothing", "apparel", "fashion", "electronics", "mobile",
        "laptop", "gadget", "croma", "reliance digital", "vijay sales",
        "decathlon", "sports"
    ],
    "Entertainment": [
        "netflix", "hotstar", "prime video", "spotify", "youtube",
        "bookmyshow", "pvr", "inox", "cinema", "movie", "theatre",
        "gaming", "playstation", "xbox", "steam", "disney", "zee5",
        "sonyliv", "jiocinema", "apple music", "concert", "event"
    ],
    "Rent": [
        "rent", "lease", "landlord", "housing", "flat rent", "pg ",
        "hostel", "accommodation"
    ],
    "Healthcare": [
        "hospital", "clinic", "doctor", "pharma", "pharmacy", "medical",
        "medicine", "apollo", "fortis", "max hospital", "medplus",
        "netmeds", "1mg", "practo", "dental", "eye care", "lab test",
        "diagnostic", "health"
    ],
    "Education": [
        "school", "college", "university", "course", "udemy", "coursera",
        "tuition", "coaching", "book", "stationery", "education"
    ],
    "Insurance": [
        "insurance", "lic", "policy", "premium", "health insurance",
        "term plan", "motor insurance"
    ],
    "EMI": [
        "emi", "loan", "installment", "bajaj finserv", "home credit"
    ],
}


def categorize_transaction(merchant_description: str, raw_category: Optional[str] = None) -> str:
    """
    Categorize a transaction based on merchant description.
    Uses raw_category from statement if available, otherwise applies rules.
    """
    if raw_category and raw_category.strip() and raw_category.strip().lower() != "other":
        normalized = raw_category.strip().title()
        valid_categories = list(CATEGORY_RULES.keys()) + ["Other"]
        if normalized in valid_categories:
            return normalized

    description_lower = merchant_description.lower()

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category

    return "Other"


def get_all_categories() -> list:
    """Return all available categories."""
    return list(CATEGORY_RULES.keys()) + ["Other"]
