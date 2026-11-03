# User Roles

## Owner/Admin
Can:
- manage business
- manage users
- manage customers
- manage products
- configure invoice settings
- create/finalize invoices
- view reports
- view audit information

## Staff
Can:
- search customers/products
- create invoices according to assigned permissions
- view/print permitted invoices

Staff cannot manage users or security settings unless explicitly granted permission.

## Authorization rule

Role checks alone are insufficient. Every query must also verify business_id ownership.
