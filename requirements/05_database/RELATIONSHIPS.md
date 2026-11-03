# MySQL Relationships

businesses 1 ─── N users
businesses 1 ─── N customers
businesses 1 ─── N products
businesses 1 ─── N invoices

customers 1 ─── N invoices

invoices 1 ─── N invoice_items
invoices 1 ─── 1 invoice_customer_snapshots
invoices 1 ─── 1 invoice_seller_snapshots

products 1 ─── N invoice_items (nullable reference)

businesses 1 ─── N invoice_sequences
businesses 1 ─── N audit_logs

Critical rule:
A historical invoice uses its snapshot tables for printed identity data. It must not dynamically read current customer/business details.
