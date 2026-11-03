# Frontend Architecture — V1

## Stack

- HTML5
- CSS3
- JavaScript (ES6+)
- Fetch API for REST calls
- Optional Jinja2 templates rendered by FastAPI

No frontend framework is required for V1.

## Structure

frontend/
  static/
    css/
      base.css
      components.css
      dashboard.css
      invoice.css
      print.css
    js/
      api.js
      auth.js
      customers.js
      products.js
      invoices.js
      dashboard.js
      settings.js
  templates/
    login.html
    dashboard.html
    customers.html
    customer-form.html
    products.html
    invoice.html
    invoice-history.html
    invoice-detail.html
    settings.html

## Design principle

Use reusable HTML components/patterns and JavaScript modules. Do not put business-critical financial rules only in browser JavaScript.

## API

Use fetch() or a small API client wrapper.

Authentication/session handling must follow the backend security design.

## Invoice

JavaScript can provide immediate UI feedback, but the backend recalculates and validates all authoritative values before saving/finalizing.

## Printing

Invoice pages use dedicated print CSS and A4 layout.

## Progressive enhancement

Where practical, pages should remain understandable without complex client-side state. Dynamic behavior should enhance the page rather than create unnecessary framework complexity.

## Future migration option

If the product eventually needs a richer SPA, React/Vue/etc. can be introduced later because the frontend communicates with a stable REST API. This is not a V1 requirement.
