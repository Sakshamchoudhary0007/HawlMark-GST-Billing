# AI Coding Agent Rules — READ FIRST

## FINAL V1 ARCHITECTURE

Use Python as the main technology. Use FastAPI + SQLAlchemy + Alembic + MySQL 8.x for the backend/data layer and HTML + CSS + JavaScript for the frontend.

AI is NOT a V1 feature. Do not add LLM APIs, vector databases, LangChain, Gemini, Claude, OpenAI or similar AI dependencies unless a future requirement explicitly authorizes them.

This file controls how an AI coding agent should work on this project.

## Absolute architecture rule

Use:
HTML + CSS + JavaScript
FastAPI
SQLAlchemy 2.x
Alembic
MySQL 8.x

DO NOT introduce MongoDB.

Do not replace MySQL with SQLite as the production architecture. SQLite may only be used for isolated tests if explicitly approved and if behavior differences are understood.

## Source of truth

Before implementing:
1. read README.md
2. read relevant module requirement
3. inspect current repository
4. inspect existing migrations
5. inspect existing tests
6. preserve working code

## Loop

PLAN
→ INSPECT
→ IMPLEMENT
→ MIGRATE
→ TEST
→ REVIEW
→ FIX
→ DOCUMENT
→ UPDATE STATUS
→ NEXT TASK

## One feature at a time

Do not implement unrelated features simultaneously.

## Database safety

Before changing schema:
- create an Alembic migration
- consider existing data
- consider indexes
- consider foreign keys
- consider backward compatibility

Never drop production data merely to fix a development error.

## Invoice safety

Never:
- use float/double for monetary values
- trust frontend totals
- generate final invoice numbers solely on the client
- modify finalized invoices through ordinary edit endpoints
- derive old invoices from current customer details

## Security

Never:
- hard-code secrets
- expose API keys
- store plaintext passwords
- trust client business_id
- allow cross-business queries

## GST

Never implement unauthorized website scraping.

Use an authorized provider abstraction.

## Testing

After each feature:
- run relevant unit tests
- run API/integration tests where applicable
- run frontend build
- run migration validation
- inspect failures
- fix failures before marking complete

## If requirements conflict

Priority:
1. data/security integrity
2. invoice/accounting correctness
3. explicit requirements
4. existing tested behavior
5. maintainability
6. visual polish

If a conflict cannot be resolved safely, record it in OPEN_QUESTIONS.md rather than inventing an accounting rule.

## Do not claim completion without evidence

A feature can only be marked [x] after its required tests/build/checks pass.

## Documentation

Update:
- IMPLEMENTATION_STATUS.md
- CHANGELOG_REQUIREMENTS.md when requirements change
- relevant module documentation


## Future AI boundary

Keep core services independent from AI. Do not create fake AI abstractions or install AI dependencies now. Future AI must call typed application services rather than directly controlling financial calculations or raw database access.
