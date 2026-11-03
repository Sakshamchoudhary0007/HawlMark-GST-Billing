from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.product import Product


def get_dashboard_summary(db: Session, business_id: int) -> Dict[str, Any]:
    # 1. Total Revenue
    revenue = db.query(func.sum(Invoice.grand_total)).filter(
        Invoice.business_id == business_id,
        Invoice.status == 'FINALIZED'
    ).scalar() or Decimal('0.0000')

    # 2. Total Invoices Count
    invoices_count = db.query(func.count(Invoice.id)).filter(
        Invoice.business_id == business_id
    ).scalar() or 0

    # 3. Total Customers Count (active)
    customers_count = db.query(func.count(Customer.id)).filter(
        Customer.business_id == business_id,
        Customer.is_archived == False
    ).scalar() or 0

    # 4. Total Products Count (active)
    products_count = db.query(func.count(Product.id)).filter(
        Product.business_id == business_id,
        Product.is_archived == False
    ).scalar() or 0

    # 5. Recent Invoices
    recent_invoices_qs = db.query(Invoice).filter(
        Invoice.business_id == business_id
    ).order_by(Invoice.created_at.desc()).limit(5).all()

    recent_invoices = []
    for inv in recent_invoices_qs:
        customer_name = ""
        if inv.customer_snapshot:
            customer_name = inv.customer_snapshot.customer_name
        elif inv.customer:
            customer_name = inv.customer.customer_name

        recent_invoices.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
            "customer_name": customer_name,
            "grand_total": str(inv.grand_total),
            "status": inv.status
        })

    # 6. Monthly Revenue (last 6 months)
    # Get revenue by year-month for FINALIZED invoices
    today = datetime.date.today()
    # Find start date of the month 5 months ago
    month_start = today.month - 5
    year_start = today.year
    if month_start <= 0:
        month_start += 12
        year_start -= 1
    six_months_ago = datetime.date(year_start, month_start, 1)

    monthly_revenue_qs = db.query(
        func.date_format(Invoice.invoice_date, '%Y-%m').label('month_str'),
        func.sum(Invoice.grand_total).label('total')
    ).filter(
        Invoice.business_id == business_id,
        Invoice.status == 'FINALIZED',
        Invoice.invoice_date >= six_months_ago
    ).group_by(
        func.date_format(Invoice.invoice_date, '%Y-%m')
    ).all()

    monthly_map = {row.month_str: Decimal(row.total) for row in monthly_revenue_qs if row.month_str}

    # Generate complete list for the last 6 months
    monthly_revenue = []
    curr_date = six_months_ago
    for _ in range(6):
        month_str = curr_date.strftime('%Y-%m')
        monthly_revenue.append({
            "month": month_str,
            "revenue": str(monthly_map.get(month_str, Decimal('0.00')))
        })
        # Advance to next month
        next_month = curr_date.month + 1
        next_year = curr_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        curr_date = datetime.date(next_year, next_month, 1)

    return {
        "total_revenue": str(revenue),
        "total_invoices": invoices_count,
        "total_customers": customers_count,
        "total_products": products_count,
        "recent_invoices": recent_invoices,
        "monthly_revenue": monthly_revenue
    }
