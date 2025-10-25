# models.py
from sqlalchemy import Table, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from database import metadata, engine

transactions = Table(
    "transactions",
    metadata,
    Column("transaction_id", String, primary_key=True),
    Column("source_account", String, nullable=False),
    Column("destination_account", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("currency", String, nullable=False),
    Column("status", String, nullable=False, default="PROCESSING"),  # PROCESSING or PROCESSED
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("processed_at", DateTime, nullable=True),
    Column("attempts", Integer, nullable=False, default=0),
    Column("last_error", Text, nullable=True),
)

def create_tables():
    metadata.create_all(engine)
