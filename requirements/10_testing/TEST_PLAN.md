# Test Plan

## Unit tests

Customer:
- create
- required fields
- GSTIN format
- duplicate handling
- search
- archive

Products:
- create
- validation
- duplicate SKU handling
- archive

Invoice calculations:
- one item
- multiple items
- quantity decimals
- rates
- GST
- CGST/SGST
- IGST
- rounding
- zero-value edge cases
- amount in words

Invoice numbering:
- first number
- sequence increment
- duplicate prevention
- concurrent requests
- financial-year scope

## Integration tests

- login
- business isolation
- customer CRUD
- product CRUD
- invoice draft
- invoice finalization
- cancellation
- GST provider failures
- MySQL transaction rollback

## End-to-end

1. Login.
2. Configure business.
3. Add customer.
4. Search by GSTIN.
5. Select customer.
6. Add products.
7. Verify calculated totals.
8. Save draft.
9. Finalize.
10. View history.
11. Print.
12. Generate PDF.
13. Modify customer master.
14. Verify old invoice remains unchanged.

## Security tests

- IDOR/cross-business access
- unauthorized endpoints
- invalid tokens
- privilege escalation
- SQL injection attempts
- malformed input
- rate limiting

## Migration tests

- clean database migration
- upgrade migration
- rollback where supported
- production-like dataset migration

## Performance

Measure:
- customer search
- invoice history
- dashboard
- invoice creation
- PDF generation

Use indexed queries and pagination.
