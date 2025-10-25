#!/usr/bin/env bash
set -e

BASE_URL="http://localhost:8000"
TXN_ID="txn_test_001"

echo "Posting webhook..."
curl -s -X POST "$BASE_URL/v1/webhooks/transactions" \
  -H "Content-Type: application/json" \
  -d "{\"transaction_id\":\"$TXN_ID\",\"source_account\":\"acc_user_1\",\"destination_account\":\"acc_merchant_1\",\"amount\":100.5,\"currency\":\"INR\"}" -i

echo
echo "Immediate GET (should be PROCESSING)..."
curl -s "$BASE_URL/v1/transactions/$TXN_ID" | jq .

echo
echo "Waiting 35s to allow processing..."
sleep 35

echo "GET after wait (should be PROCESSED)..."
curl -s "$BASE_URL/v1/transactions/$TXN_ID" | jq .
