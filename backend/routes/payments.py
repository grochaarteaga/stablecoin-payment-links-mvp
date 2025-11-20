from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from services.supabase import get_supabase_client
from utils.id_generator import generate_invoice_id
import os

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")


class InvoiceCreate(BaseModel):
    amount: float
    currency: str = Field(..., description="Fiat currency, e.g. USD, EUR, PEN")
    memo: Optional[str] = None
    merchant_wallet: str


class Invoice(BaseModel):
    id: str
    amount: float
    currency: str
    memo: Optional[str]
    merchant_wallet: str
    status: str
    payment_link: str


@router.post("/invoices", response_model=Invoice)
def create_invoice(payload: InvoiceCreate):
    supabase = get_supabase_client()
    invoice_id = generate_invoice_id()

    payment_link = f"{FRONTEND_URL}/?invoice_id={invoice_id}"

    data = {
        "id": invoice_id,
        "amount": payload.amount,
        "currency": payload.currency,
        "memo": payload.memo,
        "merchant_wallet": payload.merchant_wallet,
        "status": "PENDING",
        "payment_link": payment_link,
    }

    res = supabase.table("invoices").insert(data).execute()
    if res.error:
        raise HTTPException(status_code=500, detail=str(res.error))

    return Invoice(**data)


@router.get("/invoices/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: str):
    supabase = get_supabase_client()
    res = supabase.table("invoices").select("*").eq("id", invoice_id).single().execute()
    if res.error or not res.data:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return Invoice(**res.data)


@router.get("/invoices", response_model=List[Invoice])
def list_invoices():
    supabase = get_supabase_client()
    res = supabase.table("invoices").select("*").order("created_at", desc=True).execute()
    if res.error:
        raise HTTPException(status_code=500, detail=str(res.error))

    return [Invoice(**row) for row in res.data]
