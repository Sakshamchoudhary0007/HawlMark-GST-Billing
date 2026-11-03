from __future__ import annotations

from typing import Tuple, List
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.invoice import Invoice, InvoiceItem, InvoiceCustomerSnapshot, InvoiceSellerSnapshot
from app.models.business import Business
from app.models.customer import Customer
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.utils.exceptions import BusinessLogicError, NotFoundError
from app.services import invoice_calc, invoice_number, audit_service


def create_draft_invoice(db: Session, business_id: int, user_id: int, data: InvoiceCreate) -> Invoice:
    calculated_items = []
    for item_data in data.items:
        calc_result = invoice_calc.calculate_line_item(
            quantity=item_data.quantity,
            rate=item_data.rate,
            discount_amount=item_data.discount_amount,
            gst_rate=item_data.gst_rate,
            tax_mode=data.tax_mode
        )
        calculated_items.append(calc_result)
    
    summary = invoice_calc.calculate_invoice_summary(calculated_items, data.tax_mode)
    
    invoice = Invoice(
        business_id=business_id,
        customer_id=data.customer_id,
        invoice_date=data.invoice_date,
        tax_mode=data.tax_mode,
        reverse_charge=data.reverse_charge,
        status='DRAFT',
        created_by=user_id,
        invoice_number=None,
        notes=data.notes,
        terms=data.terms,
        subtotal=summary['subtotal'],
        taxable_amount=summary['taxable_amount'],
        cgst_amount=summary['cgst_amount'],
        sgst_amount=summary['sgst_amount'],
        igst_amount=summary['igst_amount'],
        round_off=summary['round_off'],
        grand_total=summary['grand_total'],
        currency='INR'
    )
    
    db.add(invoice)
    db.flush()
    
    for i, (item_data, calc_res) in enumerate(zip(data.items, calculated_items), start=1):
        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item_data.product_id,
            line_number=i,
            description=item_data.description,
            cat=item_data.cat,
            hsn_sac=item_data.hsn_sac,
            quantity=item_data.quantity,
            unit=item_data.unit,
            rate=item_data.rate,
            discount_amount=item_data.discount_amount,
            gst_rate=item_data.gst_rate,
            taxable_amount=calc_res['taxable_amount'],
            cgst_amount=calc_res['cgst_amount'],
            sgst_amount=calc_res['sgst_amount'],
            igst_amount=calc_res['igst_amount'],
            total_amount=calc_res['total_amount']
        )
        db.add(invoice_item)
        
    audit_service.log_action(db=db, business_id=business_id, user_id=user_id, action='CREATE_DRAFT_INVOICE', entity_type='Invoice', entity_id=invoice.id)
    db.commit()
    db.refresh(invoice)
    
    return invoice


def update_draft_invoice(db: Session, business_id: int, invoice_id: int, data: InvoiceUpdate, user_id: int = 0) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.business_id == business_id).first()
    if not invoice:
        raise NotFoundError("Invoice not found")
        
    if invoice.status != 'DRAFT':
        raise BusinessLogicError("Only draft invoices can be edited")
        
    if data.customer_id is not None:
        invoice.customer_id = data.customer_id
    if data.invoice_date is not None:
        invoice.invoice_date = data.invoice_date
    if data.tax_mode is not None:
        invoice.tax_mode = data.tax_mode
    if data.reverse_charge is not None:
        invoice.reverse_charge = data.reverse_charge
    if data.notes is not None:
        invoice.notes = data.notes
    if data.terms is not None:
        invoice.terms = data.terms
        
    if data.items is not None:
        db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).delete()
        
        calculated_items = []
        for item_data in data.items:
            calc_result = invoice_calc.calculate_line_item(
                quantity=item_data.quantity,
                rate=item_data.rate,
                discount_amount=item_data.discount_amount,
                gst_rate=item_data.gst_rate,
                tax_mode=invoice.tax_mode
            )
            calculated_items.append(calc_result)
            
        summary = invoice_calc.calculate_invoice_summary(calculated_items, invoice.tax_mode)
        
        invoice.subtotal = summary['subtotal']
        invoice.taxable_amount = summary['taxable_amount']
        invoice.cgst_amount = summary['cgst_amount']
        invoice.sgst_amount = summary['sgst_amount']
        invoice.igst_amount = summary['igst_amount']
        invoice.round_off = summary['round_off']
        invoice.grand_total = summary['grand_total']
        
        for i, (item_data, calc_res) in enumerate(zip(data.items, calculated_items), start=1):
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item_data.product_id,
                line_number=i,
                description=item_data.description,
                cat=item_data.cat,
                hsn_sac=item_data.hsn_sac,
                quantity=item_data.quantity,
                unit=item_data.unit,
                rate=item_data.rate,
                discount_amount=item_data.discount_amount,
                gst_rate=item_data.gst_rate,
                taxable_amount=calc_res['taxable_amount'],
                cgst_amount=calc_res['cgst_amount'],
                sgst_amount=calc_res['sgst_amount'],
                igst_amount=calc_res['igst_amount'],
                total_amount=calc_res['total_amount']
            )
            db.add(invoice_item)
            
    audit_service.log_action(db=db, business_id=business_id, user_id=user_id, action='UPDATE_DRAFT_INVOICE', entity_type='Invoice', entity_id=invoice.id)
    db.commit()
    db.refresh(invoice)
    return invoice


def finalize_invoice(db: Session, business_id: int, invoice_id: int, user_id: int = 0) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.business_id == business_id).first()
    if not invoice:
        raise NotFoundError("Invoice not found")
        
    if invoice.status != 'DRAFT':
        raise BusinessLogicError("Invoice is not in draft state")
        
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).order_by(InvoiceItem.line_number).all()
    calculated_items = []
    for item in items:
        calc_result = invoice_calc.calculate_line_item(
            quantity=item.quantity,
            rate=item.rate,
            discount_amount=item.discount_amount,
            gst_rate=item.gst_rate,
            tax_mode=invoice.tax_mode
        )
        calculated_items.append(calc_result)
        
        item.taxable_amount = calc_result['taxable_amount']
        item.cgst_amount = calc_result['cgst_amount']
        item.sgst_amount = calc_result['sgst_amount']
        item.igst_amount = calc_result['igst_amount']
        item.total_amount = calc_result['total_amount']
        
    summary = invoice_calc.calculate_invoice_summary(calculated_items, invoice.tax_mode)
    invoice.subtotal = summary['subtotal']
    invoice.taxable_amount = summary['taxable_amount']
    invoice.cgst_amount = summary['cgst_amount']
    invoice.sgst_amount = summary['sgst_amount']
    invoice.igst_amount = summary['igst_amount']
    invoice.round_off = summary['round_off']
    invoice.grand_total = summary['grand_total']

    number = invoice_number.generate_next_invoice_number(db, business_id, invoice.invoice_date)
    invoice.invoice_number = number
    invoice.status = 'FINALIZED'
    invoice.finalized_at = func.now()

    if invoice.customer_id:
        customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
        if customer:
            cust_snap = InvoiceCustomerSnapshot(
                invoice_id=invoice.id,
                customer_name=customer.customer_name,
                gstin=customer.gstin,
                licence_number=customer.licence_number,
                pan_number=customer.pan_number,
                mobile=customer.mobile,
                email=customer.email,
                address_line1=customer.address_line1,
                address_line2=customer.address_line2,
                city=customer.city,
                state=customer.state,
                state_code=customer.state_code,
                pincode=customer.pincode,
                place_of_supply=customer.place_of_supply,
                taxpayer_type=customer.taxpayer_type
            )
            db.add(cust_snap)
            
    business = db.query(Business).filter(Business.id == business_id).first()
    if business:
        seller_snap = InvoiceSellerSnapshot(
            invoice_id=invoice.id,
            legal_name=business.legal_name,
            trade_name=business.trade_name,
            gstin=business.gstin,
            pan=business.pan,
            phone=business.phone,
            email=business.email,
            address_line1=business.address_line1,
            address_line2=business.address_line2,
            city=business.city,
            state=business.state,
            state_code=business.state_code,
            pincode=business.pincode,
            licence_number=business.licence_number,
            logo_url=business.logo_url,
            bank_name=business.bank_name,
            bank_account_number=business.bank_account_number,
            bank_ifsc=business.bank_ifsc,
            bank_branch=business.bank_branch,
            signatory_name=business.signatory_name
        )
        db.add(seller_snap)
    
    audit_service.log_action(db=db, business_id=business_id, user_id=user_id, action='FINALIZE_INVOICE', entity_type='Invoice', entity_id=invoice.id)
    db.commit()
    db.refresh(invoice)
    return invoice


def cancel_invoice(db: Session, business_id: int, invoice_id: int, user_id: int = 0) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.business_id == business_id).first()
    if not invoice:
        raise NotFoundError("Invoice not found")
        
    if invoice.status == 'CANCELLED':
        raise BusinessLogicError("Invoice is already cancelled")
        
    invoice.status = 'CANCELLED'
    
    audit_service.log_action(db=db, business_id=business_id, user_id=user_id, action='CANCEL_INVOICE', entity_type='Invoice', entity_id=invoice.id)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice(db: Session, business_id: int, invoice_id: int) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.business_id == business_id).first()
    if not invoice:
        raise NotFoundError("Invoice not found")
    return invoice


def list_invoices(
    db: Session, business_id: int, 
    customer_id: int | None = None, 
    status: str | None = None, 
    date_from: date | None = None, 
    date_to: date | None = None, 
    q: str | None = None, 
    page: int = 1, 
    limit: int = 20
) -> Tuple[List[Invoice], int]:
    query = db.query(Invoice).filter(Invoice.business_id == business_id)
    
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    if status:
        query = query.filter(Invoice.status == status)
    if date_from:
        query = query.filter(Invoice.invoice_date >= date_from)
    if date_to:
        query = query.filter(Invoice.invoice_date <= date_to)
    if q:
        query = query.filter(Invoice.invoice_number.ilike(f"%{q}%"))
        
    total = query.count()
    items = query.order_by(Invoice.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return items, total


def delete_invoice(db: Session, business_id: int, invoice_id: int) -> None:
    invoice = get_invoice(db, business_id, invoice_id)
    db.delete(invoice)
    db.commit()

