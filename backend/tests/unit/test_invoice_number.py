import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.services.invoice_number import get_financial_year, generate_next_invoice_number
from app.models.invoice_sequence import InvoiceSequence
from app.models.business import Business

def test_get_financial_year():
    # April
    assert get_financial_year(date(2026, 4, 1)) == "2026-2027"
    # December
    assert get_financial_year(date(2026, 12, 31)) == "2026-2027"
    # January
    assert get_financial_year(date(2027, 1, 1)) == "2026-2027"
    # March
    assert get_financial_year(date(2027, 3, 31)) == "2026-2027"
    # Leap year scenario
    assert get_financial_year(date(2024, 2, 29)) == "2023-2024"

def test_generate_next_invoice_number_first_invoice(db_session: Session):
    # Setup test business
    business = Business(legal_name="Test Business", invoice_prefix="INV")
    db_session.add(business)
    db_session.commit()
    
    invoice_date = date(2026, 9, 22)
    # first invoice
    invoice_num = generate_next_invoice_number(db_session, business.id, invoice_date)
    assert invoice_num == "INV/2026-2027/00001"
    
    # check db
    seq = db_session.query(InvoiceSequence).filter_by(business_id=business.id).first()
    assert seq is not None
    assert seq.next_number == 2
    assert seq.financial_year == "2026-2027"

def test_generate_next_invoice_number_subsequent(db_session: Session):
    business = Business(legal_name="Test Business", invoice_prefix="INV")
    db_session.add(business)
    db_session.commit()
    
    invoice_date = date(2026, 9, 22)
    # initial setup
    seq = InvoiceSequence(business_id=business.id, financial_year="2026-2027", prefix="INV", next_number=15)
    db_session.add(seq)
    db_session.commit()
    
    invoice_num = generate_next_invoice_number(db_session, business.id, invoice_date)
    assert invoice_num == "INV/2026-2027/00015"
    
    seq_after = db_session.query(InvoiceSequence).filter_by(business_id=business.id).first()
    assert seq_after.next_number == 16

def test_financial_year_boundary_transitions(db_session: Session):
    business = Business(legal_name="Test Business")
    db_session.add(business)
    db_session.commit()
    
    # End of FY
    date1 = date(2026, 3, 31)
    num1 = generate_next_invoice_number(db_session, business.id, date1)
    assert num1 == "INV/2025-2026/00001"
    
    # Start of new FY
    date2 = date(2026, 4, 1)
    num2 = generate_next_invoice_number(db_session, business.id, date2)
    assert num2 == "INV/2026-2027/00001"
    
    # They should create two separate sequences
    seqs = db_session.query(InvoiceSequence).filter_by(business_id=business.id).all()
    assert len(seqs) == 2

def test_custom_prefixes(db_session: Session):
    business = Business(legal_name="Test Business", invoice_prefix="DEFAULT")
    db_session.add(business)
    db_session.commit()
    
    invoice_date = date(2026, 9, 22)
    
    # With explicit prefix overriding the business default
    num1 = generate_next_invoice_number(db_session, business.id, invoice_date, prefix="BILL")
    assert num1 == "BILL/2026-2027/00001"
    
    # With explicit prefix again
    num2 = generate_next_invoice_number(db_session, business.id, invoice_date, prefix="TAX")
    assert num2 == "TAX/2026-2027/00001"
    
    # Fallback to business default
    num3 = generate_next_invoice_number(db_session, business.id, invoice_date)
    assert num3 == "DEFAULT/2026-2027/00001"
    
    # Subseq for BILL
    num4 = generate_next_invoice_number(db_session, business.id, invoice_date, prefix="BILL")
    assert num4 == "BILL/2026-2027/00002"
