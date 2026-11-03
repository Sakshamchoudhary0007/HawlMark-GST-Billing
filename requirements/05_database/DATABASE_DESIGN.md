# MySQL Database Design

## Database decision

Use MySQL 8.x as the primary and authoritative relational database.

Do NOT use MongoDB for this project.

## Why MySQL

Billing has strong relational requirements:
- customers belong to businesses
- invoices belong to businesses and customers
- invoice items belong to invoices
- products can be reused across invoices
- users belong to businesses
- invoice numbering requires transactional consistency
- reporting needs relational queries
- financial values require strict numeric types
- foreign keys and constraints protect data integrity

## Core tables

### businesses
- id BIGINT UNSIGNED PK
- legal_name VARCHAR(255) NOT NULL
- trade_name VARCHAR(255)
- gstin VARCHAR(15)
- pan VARCHAR(10)
- phone VARCHAR(30)
- email VARCHAR(255)
- address_line1 VARCHAR(255)
- address_line2 VARCHAR(255)
- city VARCHAR(100)
- state VARCHAR(100)
- state_code VARCHAR(5)
- pincode VARCHAR(10)
- logo_url VARCHAR(500)
- created_at DATETIME
- updated_at DATETIME

### users
- id BIGINT UNSIGNED PK
- business_id BIGINT UNSIGNED FK
- name VARCHAR(150)
- email VARCHAR(255)
- password_hash VARCHAR(255)
- role VARCHAR(30)
- is_active BOOLEAN
- created_at DATETIME
- updated_at DATETIME
- UNIQUE(business_id, email)

### customers
- id BIGINT UNSIGNED PK
- business_id BIGINT UNSIGNED FK
- customer_name VARCHAR(255)
- gstin VARCHAR(15)
- licence_number VARCHAR(100)
- pan_number VARCHAR(10)
- mobile VARCHAR(30)
- email VARCHAR(255)
- address_line1 VARCHAR(255)
- address_line2 VARCHAR(255)
- city VARCHAR(100)
- state VARCHAR(100)
- state_code VARCHAR(5)
- pincode VARCHAR(10)
- place_of_supply VARCHAR(150)
- taxpayer_type VARCHAR(50)
- gst_verification_status VARCHAR(40)
- gst_verified_at DATETIME NULL
- is_archived BOOLEAN
- created_at DATETIME
- updated_at DATETIME

Indexes:
- business_id + customer_name
- business_id + gstin
- business_id + licence_number
- business_id + mobile

GSTIN uniqueness should be enforced within a business where business rules require it. NULL/blank handling must be deliberate.

### products
- id BIGINT UNSIGNED PK
- business_id BIGINT UNSIGNED FK
- name VARCHAR(255)
- sku VARCHAR(100)
- hsn_sac VARCHAR(20)
- unit VARCHAR(30)
- default_rate DECIMAL(19,4)
- gst_rate DECIMAL(5,2)
- category VARCHAR(100)
- is_archived BOOLEAN
- created_at DATETIME
- updated_at DATETIME

### invoice_sequences
- id BIGINT UNSIGNED PK
- business_id BIGINT UNSIGNED FK
- financial_year VARCHAR(20)
- prefix VARCHAR(30)
- next_number BIGINT UNSIGNED
- UNIQUE(business_id, financial_year, prefix)

### invoices
- id BIGINT UNSIGNED PK
- business_id BIGINT UNSIGNED FK
- customer_id BIGINT UNSIGNED FK NULL where allowed by business workflow
- invoice_number VARCHAR(100)
- invoice_date DATE
- tax_mode VARCHAR(20)
- reverse_charge BOOLEAN
- subtotal DECIMAL(19,4)
- taxable_amount DECIMAL(19,4)
- cgst_amount DECIMAL(19,4)
- sgst_amount DECIMAL(19,4)
- igst_amount DECIMAL(19,4)
- round_off DECIMAL(19,4)
- grand_total DECIMAL(19,4)
- currency CHAR(3)
- status VARCHAR(30)
- notes TEXT
- terms TEXT
- created_by BIGINT UNSIGNED FK
- finalized_at DATETIME NULL
- created_at DATETIME
- updated_at DATETIME
- UNIQUE(business_id, invoice_number)

### invoice_items
- id BIGINT UNSIGNED PK
- invoice_id BIGINT UNSIGNED FK
- product_id BIGINT UNSIGNED NULL
- line_number INT
- description VARCHAR(500)
- hsn_sac VARCHAR(20)
- quantity DECIMAL(19,4)
- unit VARCHAR(30)
- rate DECIMAL(19,4)
- discount_amount DECIMAL(19,4)
- taxable_amount DECIMAL(19,4)
- gst_rate DECIMAL(5,2)
- cgst_amount DECIMAL(19,4)
- sgst_amount DECIMAL(19,4)
- igst_amount DECIMAL(19,4)
- total_amount DECIMAL(19,4)

### invoice_customer_snapshots
Purpose: preserve historical buyer information.

- id BIGINT UNSIGNED PK
- invoice_id BIGINT UNSIGNED UNIQUE FK
- customer_name VARCHAR(255)
- gstin VARCHAR(15)
- licence_number VARCHAR(100)
- pan_number VARCHAR(10)
- address fields
- place_of_supply
- taxpayer_type

### invoice_seller_snapshots
Purpose: preserve historical seller information.

- id BIGINT UNSIGNED PK
- invoice_id BIGINT UNSIGNED UNIQUE FK
- legal_name
- trade_name
- gstin
- pan
- address fields
- contact details
- bank details that are intended to appear on that invoice

## Audit logs

### audit_logs
- id
- business_id
- user_id
- action
- entity_type
- entity_id
- created_at
- metadata JSON

Do not store secrets.

## Foreign keys

Use foreign keys wherever appropriate.

Deletion behavior must be deliberate:
- finalized invoices should not be physically deleted by ordinary users
- master data should generally be archived rather than deleted when referenced historically

## Migrations

Every schema change must use Alembic.

Never manually alter production schema without recording the migration.

## Character set

Use:
- utf8mb4
- appropriate utf8mb4 collation

This is important because invoices may contain Hindi and English text.

## Time

Store timestamps consistently, preferably UTC at the database/application boundary, while displaying in the business/user timezone.

Invoice date is a business date and should be treated separately from created_at.
