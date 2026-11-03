from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from app.models.invoice_sequence import InvoiceSequence
from app.models.business import Business

def get_financial_year(invoice_date: date) -> str:
    """
    Get Indian Financial Year for a given date.
    April 1 of year Y to March 31 of year Y+1.
    """
    year = invoice_date.year
    if invoice_date.month >= 4:
        return f"{year}-{year + 1}"
    else:
        return f"{year - 1}-{year}"

def generate_next_invoice_number(
    db: Session, business_id: int, invoice_date: date, prefix: Optional[str] = None
) -> str:
    """
    Generate the next invoice number for a given business safely using SELECT ... FOR UPDATE.
    """
    fy = get_financial_year(invoice_date)
    
    if not prefix:
        business = db.query(Business).filter(Business.id == business_id).first()
        if business and business.invoice_prefix:
            prefix = business.invoice_prefix
        else:
            prefix = "INV"
            
    seq = db.query(InvoiceSequence).filter(
        InvoiceSequence.business_id == business_id,
        InvoiceSequence.financial_year == fy,
        InvoiceSequence.prefix == prefix
    ).with_for_update().first()
    
    if not seq:
        seq = InvoiceSequence(
            business_id=business_id,
            financial_year=fy,
            prefix=prefix,
            next_number=2
        )
        db.add(seq)
        current_number = 1
    else:
        current_number = seq.next_number
        seq.next_number += 1
        
    db.flush()
    return f"{prefix}/{fy}/{current_number:05d}"
