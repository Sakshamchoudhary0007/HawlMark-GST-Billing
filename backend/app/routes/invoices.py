from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse
from app.services import invoice_service
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services import pdf_service
from fastapi import Response
router = APIRouter()

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    user_id = current_user.id
    return invoice_service.create_draft_invoice(db, business_id, user_id, data)

@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    user_id = current_user.id
    return invoice_service.update_draft_invoice(db, business_id, invoice_id, data)

@router.post("/invoices/{invoice_id}/finalize", response_model=InvoiceResponse)
def finalize_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    user_id = current_user.id
    return invoice_service.finalize_invoice(db, business_id, invoice_id)

@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceResponse)
def cancel_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    user_id = current_user.id
    return invoice_service.cancel_invoice(db, business_id, invoice_id)

@router.get("/invoices", response_model=InvoiceListResponse)
def list_invoices(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    items, total = invoice_service.list_invoices(
        db, business_id, customer_id, status, date_from, date_to, q, page, limit
    )
    pages = (total + limit - 1) // limit if total > 0 else 0
    return InvoiceListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    return invoice_service.get_invoice(db, business_id, invoice_id)

@router.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    invoice = invoice_service.get_invoice(db, business_id, invoice_id)
    pdf_bytes = pdf_service.generate_invoice_pdf(invoice)
    
    filename = f"Invoice-{invoice.invoice_number or invoice.id}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

@router.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business_id = current_user.business_id
    invoice_service.delete_invoice(db, business_id, invoice_id)
    return {"message": "Invoice deleted successfully"}

