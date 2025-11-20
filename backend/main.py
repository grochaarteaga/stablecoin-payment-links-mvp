from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import payments

app = FastAPI(title="Stablecoin Payment Links API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later: restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "API is running"}

# Include payments router
app.include_router(payments.router, prefix="/api", tags=["payments"])
