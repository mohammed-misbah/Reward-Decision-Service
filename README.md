# Reward Decision Service

## Overview

This project is a FastAPI-based Reward Decision microservice.

It returns a **deterministic** and **idempotent** reward decision for each transaction.  
The same input will always produce the same output.

This service is built to demonstrate backend engineering fundamentals such as correctness, scalability thinking, clean architecture, and performance discipline.

---

## Features

- FastAPI backend service
- Deterministic reward decision logic
- Idempotent request handling
- Config-driven policy evaluation using YAML
- Redis-first caching with in-memory fallback
- Daily CAC (cash reward) cap enforcement
- Cooldown after receiving a reward
- Deterministic weighted GOLD reward selection
- Unit tests using pytest
- Simple async load test

---

## API Contract

POST /reward/decide

Content-Type: application/json


### Daily CAC Cap
- Monetary rewards are tracked per user per day.
- Once the daily cap is reached, monetary rewards are blocked.
- XP is returned instead.

### Cooldown
- After receiving a monetary or GOLD reward, a user enters a cooldown period.
- During cooldown, only XP rewards are allowed.

### GOLD Reward
- GOLD rewards are selected using a deterministic weighted algorithm.
- Only eligible personas can receive GOLD.
- GOLD does not carry a monetary value.

---

## Configuration

All business rules are defined in:

config/policy.yaml

The configuration includes:
- XP per rupee
- Maximum XP per transaction
- Persona multipliers
- Daily CAC caps
- Reward weights
- Idempotency TTL
- Cooldown duration
- Feature flags (prefer XP mode)

No business logic is hard-coded.

---

## Architecture Overview

FastAPI → Cache (Redis / Memory) → Policy Engine → Deterministic Decision


## Caching

- Redis is used if available.
- If Redis is not available, the service falls back to an in-memory cache.
- In-memory cache is intended for local or development use only and is not safe for multi-process production environments.

---

## Idempotency

Requests are idempotent using a composite key:

txn_id + user_id + merchant_id

The response is cached for a configurable TTL.
Repeated requests with the same key return the cached decision.

Deterministic decisions are keyed by:
(txn_id, user_id, merchant_id)


## Determinism Guarantee

All reward decisions are derived from:
- Request fields
- Policy configuration
- Deterministic hashing (no randomness)

No time-based or non-deterministic inputs are used.
The same request will always produce the same output.


## Validation & Errors

- Request validation is enforced using Pydantic request/response schemas.
- Unsupported transaction types (non UPI/CARD) return 4xx errors.
- Invalid requests return appropriate 4xx responses.

## Assumptions & Limitations

- In-memory cache is not safe for multi-worker production setups.
- Redis is required for horizontal scalability.
- The service is stateless aside from cache usage.

## Load Testing

Target throughput: ~300 requests/sec locally (single process)


## Running the Service

### Install dependencies

```bash
pip install -r requirements.txt
```


### Request Body

```json
{
  "txn_id": "string",
  "user_id": "string",
  "merchant_id": "string",
  "amount": 500,
  "txn_type": "UPI | CARD",
  "ts": "ISO-8601 timestamp"
}
```

### Response Body
```json
{
  "decision_id": "uuid",
  "policy_version": "v1",
  "reward_type": "XP | CHECKOUT | GOLD",
  "reward_value": 0,
  "xp": 50,
  "reason_codes": [],
  "meta": {
    "persona": "RETURNING",
    "cooldown_active": false
  }
}
```

### Start the server

```bash
uvicorn app.main:app --reload
```

### Access the Payment Service UI locally at the following URL after starting the server:

http://127.0.0.1:8000/home/

### Running Unit Tests

```bash
pytest -v


Unit tests validate:

- Reward decision logic

- Idempotency behavior

- Daily CAC cap enforcement

### Additional tests cover:

- Cooldown behavior

- GOLD determinism

- Cache backend behavior

### Running Load Test

python app/load_test.py

## The script reports:

- Total requests

- Requests per second

- P95 latency

- P99 latency


## Non-Goals

- No persistent database
- No background workers
- No external reward settlement
