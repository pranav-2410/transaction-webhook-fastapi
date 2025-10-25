# Transaction Webhook Assessment — FastAPI Starter

Simple FastAPI implementation for the assessment:
- `POST /v1/webhooks/transactions` — accepts transaction JSON, returns `202 Accepted` quickly.
- Background processing simulates ~30s work then marks transaction `PROCESSED`.
- Idempotent by `transaction_id` (DB primary key).
- `GET /v1/transactions/{transaction_id}` — read status.
- `GET /` — health check with current UTC time.

## Quick start (local, recommended)