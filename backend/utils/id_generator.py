import uuid


def generate_invoice_id() -> str:
    """
    Simple unique ID for invoices.
    You can later switch to something more human friendly.
    """
    return f"INV-{uuid.uuid4().hex[:10].upper()}"
