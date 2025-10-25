# main.py
import time
import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field
from database import SessionLocal
from models import transactions, create_tables
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

app = FastAPI(title="Transaction Webhook Assessment")
create_tables()

class WebhookPayload(BaseModel):
    transaction_id: str = Field(..., example="txn_abc123def456")
    source_account: str
    destination_account: str
    amount: float
    currency: str

@app.get("/")
def health():
    return {"status": "HEALTHY", "current_time": datetime.datetime.utcnow().isoformat() + "Z"}

def process_transaction_background(transaction_id: str):
    db = SessionLocal()
    try:
        row = db.execute(select(transactions).where(transactions.c.transaction_id == transaction_id)).first()
        if not row:
            return
        current_status = row[0].status
        if current_status == "PROCESSED":
            return
        # simulate 30s external processing
        time.sleep(30)
        db.execute(
            update(transactions)
            .where(transactions.c.transaction_id == transaction_id)
            .values(status="PROCESSED", processed_at=datetime.datetime.utcnow())
        )
        db.commit()
    except Exception as e:
        # store error details and increment attempts
        db.execute(
            update(transactions)
            .where(transactions.c.transaction_id == transaction_id)
            .values(last_error=str(e))
        )
        db.commit()
    finally:
        db.close()

@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED)
def receive_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        stmt = insert(transactions).values(
            transaction_id=payload.transaction_id,
            source_account=payload.source_account,
            destination_account=payload.destination_account,
            amount=payload.amount,
            currency=payload.currency,
            status="PROCESSING",
            created_at=datetime.datetime.utcnow()
        )
        db.execute(stmt)
        db.commit()
        background_tasks.add_task(process_transaction_background, payload.transaction_id)
    except IntegrityError:
        db.rollback()
        result = db.execute(select(transactions).where(transactions.c.transaction_id == payload.transaction_id)).first()
        if result:
            row = result._mapping  # this gives you a dictionary-like row
            if row["status"] != "PROCESSED":
                background_tasks.add_task(process_transaction_background, payload.transaction_id)

    finally:
        db.close()
    return {}

@app.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    db = SessionLocal()
    result = db.execute(select(transactions).where(transactions.c.transaction_id == transaction_id)).first()
    db.close()

    if not result:
        raise HTTPException(status_code=404, detail="transaction not found")

    row = result._mapping  # access columns safely

    return {
        "transaction_id": row["transaction_id"],
        "source_account": row["source_account"],
        "destination_account": row["destination_account"],
        "amount": row["amount"],
        "currency": row["currency"],
        "status": row["status"],
        "created_at": (row["created_at"].isoformat() + "Z") if row["created_at"] else None,
        "processed_at": (row["processed_at"].isoformat() + "Z") if row["processed_at"] else None,
    }
