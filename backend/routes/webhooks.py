# backend/routes/webhooks.py

"""
Improved Alchemy Webhook Listener
---------------------------------
Receives Base USDC Transfer events:
- Extract from/to and amount from logs
- Match invoice using wallet + amount tolerance
- Mark invoice as PAID
- Avoid duplicate updates
- Clean structured logging
"""

from fastapi import APIRouter, Request
from services.supabase import get_supabase_client
import os
from decimal import Decimal

router = APIRouter()

# Correct USDC contract for Base
USDC_BASE = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913".lower()


def decode_topic_address(topic_hex: str) -> str:
    """Decode a padded 32-byte hex topic into an address."""
    return "0x" + topic_hex[-40:]


@router.post("/alchemy")
async def alchemy_webhook(request: Request):
    """Main webhook listener for Alchemy."""
    print("\n---------------- WEBHOOK RECEIVED ----------------")

    try:
        body = await request.json()
    except Exception:
        print("❌ Could not decode webhook body")
        return {"status": "ignored"}

    # Extract logs
    try:
        logs = body["event"]["data"]["block"]["logs"]
    except Exception:
        print("❌ No logs found in webhook JSON")
        return {"status": "ignored"}

    supabase = get_supabase_client()

    for log in logs:

        contract = log["account"]["address"].lower()
        if contract != USDC_BASE:
            print(f"⚠️ Ignored non-USDC contract: {contract}")
            continue

        topics = log.get("topics", [])
        if len(topics) < 3:
            print("❌ Invalid Transfer log: missing indexed topics")
            continue

        # Decode from, to
        from_addr = decode_topic_address(topics[1]).lower()
        to_addr = decode_topic_address(topics[2]).lower()

        # Decode amount
        data_hex = log.get("data", "0x0")
        amount_raw = int(data_hex, 16)
        amount = Decimal(amount_raw) / Decimal(1_000_000)

        print(f"🟢 USDC Transfer detected:")
        print(f"    From:    {from_addr}")
        print(f"    To:      {to_addr}")
        print(f"    Amount:  {amount}")

        # 🔍 Find pending invoices with this wallet
        wallet_matches = (
            supabase.table("invoices")
            .select("*")
            .eq("merchant_wallet", to_addr)
            .eq("status", "PENDING")
            .execute()
        )

        if not wallet_matches.data:
            print("❌ No PENDING invoices for this wallet")
            continue

        print(f"🔎 Found {len(wallet_matches.data)} pending invoice(s) for wallet")

        # Try to match by amount within tolerance
        TOLERANCE = Decimal("0.000001")
        matched_invoice = None

        for inv in wallet_matches.data:
            inv_amount = Decimal(str(inv["amount"]))
            if abs(inv_amount - amount) <= TOLERANCE:
                matched_invoice = inv
                break

        if not matched_invoice:
            print("❌ No invoice matching the exact amount")
            continue

        invoice_id = matched_invoice["id"]
        print(f"🎯 Matching invoice found: {invoice_id}")

        # Prevent double-updating
        if matched_invoice["status"] == "PAID":
            print(f"⚠️ Invoice {invoice_id} already PAID — skipping")
            continue

        # Update invoice
        supabase.table("invoices").update({"status": "PAID"}).eq("id", invoice_id).execute()

        print(f"🎉 SUCCESS → Invoice {invoice_id} marked as PAID")

    print("--------------- END WEBHOOK ----------------\n")
    return {"status": "ok"}
