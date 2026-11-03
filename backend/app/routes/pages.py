"""
Page routes — serve Jinja2 HTML templates.

These routes deliver the frontend HTML pages. They do NOT contain
business logic; the pages load data via JavaScript calling the REST API.
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])

# Resolve templates directory relative to project root
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Render the login page."""
    return templates.TemplateResponse(request, "login.html")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> HTMLResponse:
    """Render the registration page."""
    return templates.TemplateResponse(request, "register.html")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request) -> HTMLResponse:
    """Render the dashboard page."""
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/customers", response_class=HTMLResponse)
async def customers_page(request: Request) -> HTMLResponse:
    """Render the customers list page."""
    return templates.TemplateResponse(request, "customers.html")


@router.get("/customers/new", response_class=HTMLResponse)
async def customer_create_page(request: Request) -> HTMLResponse:
    """Render the customer creation form."""
    return templates.TemplateResponse(request, "customer_form.html")


@router.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def customer_edit_page(request: Request, customer_id: int) -> HTMLResponse:
    """Render the customer edit form."""
    return templates.TemplateResponse(request, "customer_form.html", {"customer_id": customer_id})



@router.get("/invoices/new", response_class=HTMLResponse)
async def invoice_create_page(request: Request) -> HTMLResponse:
    """Render the invoice creation page."""
    return templates.TemplateResponse(request, "invoice_create.html")


@router.get("/invoices", response_class=HTMLResponse)
async def invoice_history_page(request: Request) -> HTMLResponse:
    """Render the invoice history / list page."""
    return templates.TemplateResponse(request, "invoice_history.html")


@router.get("/invoices/{invoice_id}/edit", response_class=HTMLResponse)
async def invoice_edit_page(request: Request, invoice_id: int) -> HTMLResponse:
    """Render the draft invoice edit form."""
    return templates.TemplateResponse(request, "invoice_create.html", {"invoice_id": invoice_id})


@router.get("/invoices/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail_page(request: Request, invoice_id: int) -> HTMLResponse:
    """Render the invoice detail / preview page."""
    return templates.TemplateResponse(request, "invoice_detail.html", {"invoice_id": invoice_id})


@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request) -> HTMLResponse:
    """Render the user management / settings page."""
    return templates.TemplateResponse(request, "settings.html")


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request) -> HTMLResponse:
    """Render the business settings and bank details page."""
    return templates.TemplateResponse(request, "settings.html")
