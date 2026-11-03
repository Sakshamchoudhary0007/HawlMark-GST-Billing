# REST API Specification

Base path: /api

## Auth
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout

## Business
GET /business
PUT /business

## Customers
GET /customers?q=&page=&limit=
POST /customers
GET /customers/{id}
PUT /customers/{id}
PATCH /customers/{id}/archive

## GST
GET /gst/lookup?gstin=

The endpoint uses an authorized provider. No unauthorized portal scraping.

## Products
GET /products?q=&page=&limit=
POST /products
GET /products/{id}
PUT /products/{id}
PATCH /products/{id}/archive

## Invoices
GET /invoices
POST /invoices
GET /invoices/{id}
PUT /invoices/{id}              # drafts only
POST /invoices/{id}/finalize
POST /invoices/{id}/cancel
GET /invoices/{id}/pdf

## Dashboard
GET /dashboard/summary

## API rules

- authentication required for business data
- every resource checked against business_id
- pagination for lists
- consistent error format
- request validation through Pydantic
- server-side calculation of invoice totals
