# Acceptance Criteria

## Customer storage

Given a user enters GSTIN, licence number and party details,
when the user saves,
then MySQL stores the customer under the authenticated business.

## Customer retrieval

Given a saved customer exists,
when the user searches by name, GSTIN or licence number,
then matching customers are returned only from the user's business.

## Auto-fill

Given a saved customer is selected,
then invoice party fields are populated from the customer record for the draft.

## GST verification

Given a GSTIN is entered,
when verification is requested,
then the backend calls the configured authorized provider and returns normalized information or a clear error state.

## Invoice calculations

Given invoice items,
when an invoice is created/finalized,
then the backend recalculates subtotal, taxable value, GST and grand total using Decimal/DECIMAL.

## Invoice numbering

Given two concurrent invoice requests,
then the system must not create duplicate finalized invoice numbers.

## Historical integrity

Given an invoice was finalized with customer address X,
when the customer master is later changed to address Y,
then the finalized invoice still displays X.

## Business isolation

Given User A belongs to Business A,
when User A requests Business B's invoice/customer/product,
then access is denied.

## Finalization

A finalized invoice cannot be modified through a normal draft update endpoint.

## Printing

The print view is A4-oriented and hides application navigation.

## PDF

PDF contains the same authoritative invoice values as the invoice detail view.

## Regression

All required tests pass before a feature is marked complete.
