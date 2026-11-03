# SQL and Data Conventions

- Use BIGINT UNSIGNED for primary keys unless there is a documented reason otherwise.
- Use DECIMAL(19,4) for monetary/quantity values where four decimal places are required.
- Use DECIMAL(5,2) for GST percentages.
- Never use FLOAT or DOUBLE for accounting amounts.
- Use NOT NULL where business rules require a value.
- Add indexes based on actual search patterns.
- Avoid unnecessary indexes that slow writes.
- Use foreign keys.
- Use parameterized SQL/SQLAlchemy expressions.
- Never construct SQL by string concatenation with user input.
- Use utf8mb4.
- Add created_at and updated_at consistently.
- Use soft archive flags for customer/product master data when appropriate.
- Finalized invoice records require controlled lifecycle operations.
