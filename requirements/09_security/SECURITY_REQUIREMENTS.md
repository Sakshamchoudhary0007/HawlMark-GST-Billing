# Security Requirements

## Authentication

- password hashing with a modern password hashing algorithm
- no plaintext passwords
- secure token handling
- account/session invalidation support

## Authorization

For every business-owned endpoint:
1. authenticate user
2. identify business_id from authenticated server-side identity
3. query only records belonging to that business
4. never trust business_id supplied by the client

## Secrets

Environment/secret management only:
- MYSQL_URL
- JWT_SECRET
- GST_PROVIDER_API_KEY
- GST_PROVIDER_BASE_URL
- other service credentials

Never commit `.env`.

## Input validation

Validate:
- IDs
- GSTIN
- PAN
- email
- mobile
- PIN
- quantities
- rates
- tax rates
- dates
- invoice statuses

## SQL safety

Use SQLAlchemy/parameterized queries.

Never concatenate user input into SQL.

## Database

- MySQL authentication enabled
- TLS for remote DB connections
- least-privilege DB account
- backups
- tested restoration procedure

## Invoice integrity

Finalized invoice data must be protected against ordinary edits.

Corrections/cancellations require explicit workflow and audit records.

## Audit log

Record:
- actor
- business
- action
- entity
- entity ID
- timestamp
- safe metadata

Do not log secrets.
