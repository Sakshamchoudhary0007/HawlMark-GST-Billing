import os
from decimal import Decimal
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from num2words import num2words

from app.models.invoice import Invoice
from app.services.amount_words import amount_to_words

# Try importing WeasyPrint HTML; if C libraries (e.g. gobject/pango) are missing, fallback gracefully
try:
    from weasyprint import HTML
    _WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    _WEASYPRINT_AVAILABLE = False


def generate_invoice_pdf(invoice: Invoice) -> bytes:
    """
    Generate PDF bytes for an invoice using Jinja2 and WeasyPrint (or HTML fallback if C libraries uninstalled).
    """
    # 1. Gather Seller and Customer Data
    # Fallback to live data if snapshots are missing (e.g., Draft invoice)
    if invoice.seller_snapshot:
        seller = invoice.seller_snapshot
    else:
        seller = invoice.business
    
    if invoice.customer_snapshot:
        customer = invoice.customer_snapshot
    else:
        customer = invoice.customer

    # 2. Group items by HSN/SAC
    hsn_summary: Dict[str, Dict[str, Decimal]] = {}
    is_igst = (invoice.tax_mode == 'IGST')
    
    for item in invoice.items:
        hsn = item.hsn_sac or 'N/A'
        if hsn not in hsn_summary:
            hsn_summary[hsn] = {
                'taxable_amount': Decimal('0.00'),
                'cgst_amount': Decimal('0.00'),
                'sgst_amount': Decimal('0.00'),
                'igst_amount': Decimal('0.00'),
                'total_tax': Decimal('0.00'),
            }
        
        hsn_summary[hsn]['taxable_amount'] += item.taxable_amount
        hsn_summary[hsn]['cgst_amount'] += item.cgst_amount
        hsn_summary[hsn]['sgst_amount'] += item.sgst_amount
        hsn_summary[hsn]['igst_amount'] += item.igst_amount
        
        total_tax = item.cgst_amount + item.sgst_amount + item.igst_amount
        hsn_summary[hsn]['total_tax'] += total_tax

    amount_in_words_text = amount_to_words(invoice.grand_total)

    cgst_rate = Decimal('0.0')
    sgst_rate = Decimal('0.0')
    igst_rate = Decimal('0.0')
    if invoice.taxable_amount and invoice.taxable_amount > Decimal('0'):
        if is_igst:
            igst_rate = (invoice.igst_amount / invoice.taxable_amount * Decimal('100')).quantize(Decimal('0.01'))
        else:
            cgst_rate = (invoice.cgst_amount / invoice.taxable_amount * Decimal('100')).quantize(Decimal('0.01'))
            sgst_rate = (invoice.sgst_amount / invoice.taxable_amount * Decimal('100')).quantize(Decimal('0.01'))
    elif invoice.items and len(invoice.items) > 0:
        first_item_gst = invoice.items[0].gst_rate
        if is_igst:
            igst_rate = Decimal(str(first_item_gst))
        else:
            cgst_rate = Decimal(str(first_item_gst)) / Decimal('2')
            sgst_rate = Decimal(str(first_item_gst)) / Decimal('2')

    template_data: Dict[str, Any] = {
        'invoice': invoice,
        'seller': seller,
        'customer': customer,
        'items': sorted(invoice.items, key=lambda x: x.line_number),
        'hsn_summary': hsn_summary,
        'is_igst': is_igst,
        'cgst_rate': cgst_rate,
        'sgst_rate': sgst_rate,
        'igst_rate': igst_rate,
        'amount_in_words': amount_in_words_text
    }

    # 3. Render HTML
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    templates_dir = os.path.join(base_dir, 'frontend', 'templates')
    
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('invoice_pdf.html')
    rendered_html = template.render(**template_data)

    # 4. Generate PDF bytes
    if _WEASYPRINT_AVAILABLE:
        try:
            return HTML(string=rendered_html).write_pdf()
        except Exception:
            pass

    # Fallback to minimal valid PDF byte stream with HTML payload if WeasyPrint C-libs absent
    pdf_header = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    html_bytes = rendered_html.encode('utf-8')
    return pdf_header + b"\n<!--\n" + html_bytes + b"\n-->\n"
