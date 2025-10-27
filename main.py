import asyncio
import datetime
from fastapi import FastAPI, HTTPException, status
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


async def process_transaction_background(transaction_id: str):
    """Asynchronous background processor for webhook transactions."""
    print(f"[{datetime.datetime.utcnow()}] Started background task for {transaction_id}")
    db = SessionLocal()
    try:
        result = db.execute(
            select(transactions).where(transactions.c.transaction_id == transaction_id)
        ).first()
        if not result:
            print(f"[{datetime.datetime.utcnow()}] Transaction not found: {transaction_id}")
            return

        row = result._mapping  # ✅ Access columns by name
        current_status = row["status"]

        if current_status == "PROCESSED":
            print(f"[{datetime.datetime.utcnow()}] Transaction already processed: {transaction_id}")
            return

        # Simulate ~30s external processing
        print(f"[{datetime.datetime.utcnow()}] Processing {transaction_id}...")
        await asyncio.sleep(30)
        print(f"[{datetime.datetime.utcnow()}] Finished waiting for {transaction_id}")

        # Update DB
        db.execute(
            update(transactions)
            .where(transactions.c.transaction_id == transaction_id)
            .values(status="PROCESSED", processed_at=datetime.datetime.utcnow())
        )
        db.commit()
        print(f"[{datetime.datetime.utcnow()}] Marked {transaction_id} as PROCESSED")

    except Exception as e:
        print(f"[{datetime.datetime.utcnow()}] Error processing {transaction_id}: {e}")
        db.rollback()
        db.execute(
            update(transactions)
            .where(transactions.c.transaction_id == transaction_id)
            .values(last_error=str(e))
        )
        db.commit()
    finally:
        db.close()



@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(payload: WebhookPayload):
    """Receives a transaction webhook and schedules async processing."""
    db = SessionLocal()
    try:
        stmt = insert(transactions).values(
            transaction_id=payload.transaction_id,
            source_account=payload.source_account,
            destination_account=payload.destination_account,
            amount=payload.amount,
            currency=payload.currency,
            status="PROCESSING",
            created_at=datetime.datetime.utcnow(),
        )
        db.execute(stmt)
        db.commit()
        print(f"[{datetime.datetime.utcnow()}] Received new transaction {payload.transaction_id}")
    except IntegrityError:
        db.rollback()
        result = db.execute(
            select(transactions).where(transactions.c.transaction_id == payload.transaction_id)
        ).first()
        if result:
            row = result._mapping
            if row["status"] == "PROCESSED":
                print(f"[{datetime.datetime.utcnow()}] Duplicate ignored (already processed): {payload.transaction_id}")
                db.close()
                return {}
            print(f"[{datetime.datetime.utcnow()}] Duplicate detected, reprocessing: {payload.transaction_id}")
    finally:
        db.close()

    # ✅ Schedule the async background task safely
    asyncio.create_task(process_transaction_background(payload.transaction_id))
    return {}


@app.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    """Fetch transaction details by ID."""
    db = SessionLocal()
    result = db.execute(
        select(transactions).where(transactions.c.transaction_id == transaction_id)
    ).first()
    db.close()

    if not result:
        raise HTTPException(status_code=404, detail="transaction not found")

    row = result._mapping
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
