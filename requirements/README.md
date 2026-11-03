# GST Billing Application — Final Master AI Development Specification

## FINAL TECHNOLOGY DECISION

This project is **Python-first**.

- Main technology: Python
- Backend: FastAPI
- Database: MySQL 8.x
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Validation: Pydantic v2
- Frontend: HTML + CSS + JavaScript
- AI: NOT included in Version 1

MongoDB is NOT used.

React is NOT required for Version 1.

AI is deliberately deferred. The architecture only needs clean extension points so future AI can be introduced without rewriting core billing functionality.

## Product purpose

Build a reliable, configurable business billing application for creating professional GST invoices, saving business/customer/product information, searching it later, calculating taxes, producing PDFs/prints, and maintaining historical invoice records.

## Core user flow

Configure business once
    ↓
Save customer with GSTIN/licence/details
    ↓
Search customer whenever needed
    ↓
Create invoice
    ↓
Select customer
    ↓
Add products/services
    ↓
Python recalculates taxes and totals
    ↓
Preview
    ↓
Save/finalize
    ↓
Print/PDF
    ↓
Invoice history/reports

## Critical principles

1. Python backend is authoritative for business rules.
2. MySQL is the authoritative persistent database.
3. Use Decimal/DECIMAL for monetary values.
4. Use transactions for atomic multi-table operations.
5. Finalized invoices are protected from ordinary edits.
6. Historical seller/buyer information is stored in invoice snapshots.
7. Invoice numbers are generated server-side and protected against duplicates.
8. Every business-owned query is scoped to the authenticated business.
9. Configuration belongs in database/settings where appropriate; secrets belong in environment/secret storage.
10. AI is not a V1 dependency.
11. Do not hard-code business-specific information from the reference invoice.
12. Current GST/tax/legal requirements must be independently validated before production.

## Reference invoice

The supplied invoice image is a visual/structural reference. It informs the invoice layout but must not cause private or business-specific values to be hard-coded.

## Definition of done

A feature is complete only when applicable:
- frontend complete
- backend complete
- MySQL schema complete
- Alembic migration complete
- validation complete
- authorization complete
- tests complete
- error/loading/empty states complete
- documentation updated
- build/tests pass
