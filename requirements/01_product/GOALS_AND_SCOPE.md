# Goals and Scope

## Primary goals

### G1 — Business profile
Store business/legal/trade details once and reuse them in invoices.

### G2 — Reusable customers
Enter GSTIN, licence number and party details once. Save them in MySQL and retrieve them by search.

### G3 — Fast billing
New Invoice → search party → select party → details auto-fill → add items → calculate → preview → save/finalize → print/PDF.

### G4 — Correct accounting data
Use MySQL transactions and DECIMAL values for financial records.

### G5 — Professional invoice
Produce a clean A4 invoice based on the supplied visual reference.

### G6 — Search and reporting
Search customers, products and invoices efficiently and provide basic sales/invoice summaries.

### G7 — Historical integrity
Editing a customer later must not change a finalized invoice's historical customer information.

## MVP modules

- Authentication
- Business profile
- Customer/party management
- Product/service management
- GSTIN verification integration
- Invoice creation
- GST calculation
- Invoice numbering
- Invoice preview
- Print
- PDF
- Invoice history
- Dashboard
- Settings
- Audit log
- Backup/recovery procedures

## Future modules

- payment tracking
- inventory
- purchase invoices
- credit/debit notes
- e-invoicing
- e-way bill
- accounting ledger
- advanced analytics
- multi-branch support

Future modules must not compromise the core invoice data model.
