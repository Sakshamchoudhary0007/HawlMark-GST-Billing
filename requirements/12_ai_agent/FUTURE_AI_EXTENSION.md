# Future AI Extension — NOT PART OF V1

AI is intentionally excluded from Version 1.

The system must nevertheless keep clean boundaries so AI can be introduced later without rewriting the billing engine.

## V1 rule

Do not install, configure, call, or depend on:
- Gemini
- OpenAI
- Claude
- LangChain
- vector databases
- LLM APIs

unless a future approved feature explicitly requires them.

## Core principle

AI may assist with interpretation, search, document extraction, analytics, or drafting.

AI must NOT become the authoritative source for:
- monetary calculations
- GST calculations
- invoice numbering
- database integrity
- authorization
- final invoice state

## Future extension point

backend/
  integrations/
    ai/

Possible future services:
- ai_service.py
- invoice_assistant.py
- document_extractor.py
- analytics_assistant.py
- natural_language_search.py

These services should communicate with existing application services through typed interfaces.

## Example future flow

User request
    ↓
AI interpretation
    ↓
Structured command
    ↓
Existing Python service
    ↓
Validation
    ↓
MySQL transaction

The existing invoice/customer/product/tax services remain usable with or without AI.

## No premature abstraction

Do not build an AI framework in V1 merely because AI may be added later. Keep only clean module boundaries and stable service interfaces.
