# GSTIN Integration

## Workflow

1. User enters GSTIN.
2. Frontend performs basic format validation.
3. User selects Verify/Fetch.
4. Backend calls an authorized GST verification/data provider.
5. Provider response is normalized by the backend.
6. Retrieved information is displayed to the user.
7. User confirms.
8. Customer is saved.

## Provider abstraction

Create:
- base provider interface
- provider adapter
- normalized response schema
- provider-specific exceptions

Example structure:

services/gst/
  base.py
  provider.py
  schemas.py
  exceptions.py

The application must not couple the customer module directly to one provider's response format.

## Possible returned fields

- GSTIN
- legal name
- trade name
- taxpayer type
- registration status/date where permitted
- principal place
- state/state code
- PIN

Only use fields legally/contractually available from the provider.

## Error states

- invalid format
- not found
- unavailable
- timeout
- rate limited
- unauthorized credentials
- partial data
- verified

## Security

Provider credentials stay in backend environment variables/secrets.

Never expose provider API keys in HTML/CSS/JavaScript.

## Legal/compliance

The software team must verify current GST/API terms and Indian tax requirements before production use. This requirements document does not itself certify tax compliance.
