# Reference Invoice → Application Mapping

| Reference concept | Application source |
|---|---|
| TAX INVOICE | invoice template |
| Business name | seller snapshot |
| Business address | seller snapshot |
| GSTIN | seller snapshot |
| Party details | customer snapshot |
| Licence No. | customer snapshot |
| Invoice No. | invoices.invoice_number |
| Date | invoices.invoice_date |
| Place of Supply | invoice/customer data |
| Description | invoice_items.description |
| HSN/SAC | invoice_items.hsn_sac |
| Qty | invoice_items.quantity |
| Unit | invoice_items.unit |
| Price | invoice_items.rate |
| Amount | calculated |
| CGST | calculated |
| SGST | calculated |
| IGST | calculated |
| Grand Total | calculated |
| Amount in words | calculated |
| Bank details | seller snapshot |
| Terms | invoice/business configuration |
| Signatures | template/business configuration |

Reference data is never hard-coded.
