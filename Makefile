.PHONY: install run docker-build docker-run test

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn main:app --reload --port 8000

docker-build:
	docker build -t tx-webhook:latest .

docker-run:
	docker run --rm -p 8000:8000 tx-webhook:latest

test:
	bash tests/test_endpoints.sh
