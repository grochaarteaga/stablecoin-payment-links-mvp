import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Stablecoin Payment Links",
    page_icon="💸",
    layout="centered",
)

st.title("💸 Stablecoin Payment Links MVP")

# Simple navigation
page = st.sidebar.radio("Navigation", ["Create Payment Request", "My Invoices"])


def create_invoice_view():
    st.header("Create Payment Request")

    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    currency = st.selectbox("Currency", ["USD", "EUR", "PEN", "BRL", "ARS"])
    memo = st.text_input("Memo / Description", "")
    merchant_wallet = st.text_input("Merchant Wallet Address (Base USDC)")

    if st.button("Create Payment Link"):
        if amount <= 0 or not merchant_wallet:
            st.error("Amount must be > 0 and wallet is required.")
            return

        payload = {
            "amount": amount,
            "currency": currency,
            "memo": memo or None,
            "merchant_wallet": merchant_wallet,
        }

        try:
            res = requests.post(f"{BACKEND_URL}/api/invoices", json=payload, timeout=10)
            res.raise_for_status()
            data = res.json()
            st.success("Payment link created!")
            st.write("**Invoice ID:**", data["id"])
            st.write("**Payment link:**")
            st.code(data["payment_link"])
        except Exception as e:
            st.error(f"Error creating invoice: {e}")


def invoices_list_view():
    st.header("My Invoices")

    try:
        res = requests.get(f"{BACKEND_URL}/api/invoices", timeout=10)
        res.raise_for_status()
        invoices = res.json()
    except Exception as e:
        st.error(f"Error fetching invoices: {e}")
        return

    if not invoices:
        st.info("No invoices yet. Create one first.")
        return

    for inv in invoices:
        with st.expander(f"{inv['id']} - {inv['amount']} {inv['currency']} ({inv['status']})"):
            st.write("**Memo:**", inv.get("memo") or "-")
            st.write("**Wallet:**", inv["merchant_wallet"])
            st.write("**Payment link:**")
            st.code(inv["payment_link"])


if page == "Create Payment Request":
    create_invoice_view()
else:
    invoices_list_view()
