# Backend Architecture

## Stack

- Python 3.11+ (select and pin a tested version)
- FastAPI
- SQLAlchemy 2.x
- Alembic
- MySQL 8.x
- Pydantic v2
- PyMySQL or mysqlclient, based on deployment/testing decision

## Layers

routes/
schemas/
services/
repositories/
models/
core/
utils/

## Responsibilities

Routes:
- HTTP handling only

Schemas:
- request/response validation

Services:
- business rules
- calculations
- invoice lifecycle

Repositories:
- SQLAlchemy database access

Models:
- database schema mappings

## Transactions

Use SQLAlchemy transactions for:
- invoice finalization
- invoice-number allocation
- operations that write multiple related rows
- any operation requiring atomicity

## Concurrency

Invoice number generation must be safe under concurrent requests.

Do not:
- SELECT a number in application code
- increment it later without a lock/transaction
- assume one user at a time

Use a transactional sequence strategy with appropriate row locking.

## Backend authority

Final invoice totals are recalculated server-side.

Never accept client totals as authoritative.

## Error response

{
  "error": {
    "code": "CUSTOMER_NOT_FOUND",
    "message": "Customer not found.",
    "details": {}
  }
}

Do not expose stack traces or secrets.

## Logging

Log:
- request ID
- authenticated user ID
- route
- status
- duration
- safe error code

Never log passwords, JWT secrets, provider API keys or unnecessary sensitive data.
