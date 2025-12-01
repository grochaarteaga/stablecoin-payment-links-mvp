# backend/services/usdc.py
"""
This module helps us validate if an incoming blockchain transaction
corresponds to a USDC payment for one of our invoices.

Alchemy will send a webhook every time USDC is transferred on Base.
We only need to check:
  - correct token address (Base USDC)
  - correct receiver (merchant wallet)
  - correct amount
"""

from decimal import Decimal

# USDC contract address on BASE mainnet
BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54Bda02913".lower()


def extract_transfer(event: dict):
    """
    Extract transfer details from the Alchemy webhook event.
    Returns a dict with:
        - from
        - to
        - value (Decimal)
        - token
    """

    # Alchemy formats logs differently depending on event
    # For stablecoin transfers, this is always present
    try:
        raw = event["event"]["data"]["item"]
        from_addr = raw["fromAddress"].lower()
        to_addr = raw["toAddress"].lower()
        token = raw["rawContract"]["address"].lower()
        value_wei = Decimal(raw["value"])  # USDC is 6 decimals
        value = value_wei / Decimal(1_000_000)

        return {
            "from": from_addr,
            "to": to_addr,
            "token": token,
            "amount": value,
        }

    except Exception as e:
        print("❌ Error parsing transfer:", e)
        return None


def is_usdc_on_base(transfer: dict):
    """
    Validate if the token sent was USDC on Base.
    """
    if not transfer:
        return False

    return transfer["token"] == BASE_USDC
