# Transaction Webhook Assessment — FastAPI Starter
Technical Choices
- FastAPI:
Chosen for its high performance, ease of use, and automatic API documentation with Swagger (/docs). FastAPI supports asynchronous endpoints, which is ideal for handling webhooks efficiently.

- SQLite:
Used as a lightweight, file-based database for simplicity and easy deployment. Ideal for small to medium-scale applications where setting up a full database server is unnecessary. Its zero-configuration nature makes development and testing straightforward.

- Uvicorn:
An ASGI server used to run the FastAPI application. It is fast, production-ready, and fully supports asynchronous execution, complementing FastAPI’s async capabilities.

- Python + Pydantic:
Python provides a robust ecosystem for backend development, and Pydantic ensures data validation and type safety for API request/response models.

Simple FastAPI implementation:
- `POST /v1/webhooks/transactions` — accepts transaction JSON, returns `202 Accepted` quickly.
- Background processing simulates ~30s work then marks transaction `PROCESSED`.
- Idempotent by `transaction_id` (DB primary key).
- `GET /v1/transactions/{transaction_id}` — read status.
- `GET /` — health check with current UTC time.
- `GET /docs` -  Interactive API documentation.

# Live API: https://transaction-webhook-fastapi-production.up.railway.app/
