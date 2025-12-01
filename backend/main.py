from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your existing payments router
from routes import payments

# NEW: import the webhooks router
from routes.webhooks import router as webhooks_router

# ---------------------------------------------------------
# 🚀 FASTAPI INIT
# ---------------------------------------------------------
app = FastAPI(title="Stablecoin Payment Links API")


# ---------------------------------------------------------
# 🌐 CORS CONFIG
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later: restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# 🧪 HEALTH CHECK
# ---------------------------------------------------------
@app.get("/ping")
def ping():
    return {"status": "ok", "message": "API is running"}


# ---------------------------------------------------------
# 🧾 PAYMENTS ROUTES
# ---------------------------------------------------------
app.include_router(
    payments.router,
    prefix="/api",
    tags=["payments"],
)


# ---------------------------------------------------------
# 🔥 WEBHOOKS ROUTES  (Alchemy → USDC events)
# ---------------------------------------------------------
app.include_router(
    webhooks_router,
    prefix="/api/webhooks",
    tags=["webhooks"],
)
