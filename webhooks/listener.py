from typing import Dict

def process_blockchain_event(payload: Dict):
    """
    Placeholder for logic that:
    - Verifies webhook signature
    - Extracts tx hash, from, to, amount, token
    - Matches against invoices by merchant_wallet + expected amount
    - Marks invoice as PAID
    """
    # TODO: implement when we connect Alchemy
    print("Received blockchain event:", payload)
