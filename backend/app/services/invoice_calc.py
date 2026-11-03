from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List
from pydantic import BaseModel

class LineItemCalc(BaseModel):
    quantity: Decimal
    rate: Decimal
    discount_amount: Decimal
    gst_rate: Decimal

def calculate_line_item(quantity: Decimal, rate: Decimal, discount_amount: Decimal, gst_rate: Decimal, tax_mode: str) -> Dict[str, Decimal]:
    subtotal = quantity * rate
    taxable_amount = max(Decimal('0.0000'), subtotal - discount_amount)
    
    cgst_amount = Decimal('0.0000')
    sgst_amount = Decimal('0.0000')
    igst_amount = Decimal('0.0000')
    
    if tax_mode == 'CGST_SGST':
        half_rate = gst_rate / Decimal('2')
        cgst_amount = (taxable_amount * half_rate / Decimal('100')).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        sgst_amount = (taxable_amount * half_rate / Decimal('100')).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    elif tax_mode == 'IGST':
        igst_amount = (taxable_amount * gst_rate / Decimal('100')).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        
    total_amount = taxable_amount + cgst_amount + sgst_amount + igst_amount
    
    return {
        'subtotal': subtotal,
        'taxable_amount': taxable_amount,
        'cgst_amount': cgst_amount,
        'sgst_amount': sgst_amount,
        'igst_amount': igst_amount,
        'total_amount': total_amount
    }

def calculate_invoice_summary(line_items: List[Dict[str, Decimal]], tax_mode: str) -> Dict[str, Decimal]:
    subtotal = Decimal('0.0000')
    taxable_amount = Decimal('0.0000')
    cgst_amount = Decimal('0.0000')
    sgst_amount = Decimal('0.0000')
    igst_amount = Decimal('0.0000')

    for item in line_items:
        subtotal += item.get('subtotal', Decimal('0.0000'))
        taxable_amount += item.get('taxable_amount', Decimal('0.0000'))
        cgst_amount += item.get('cgst_amount', Decimal('0.0000'))
        sgst_amount += item.get('sgst_amount', Decimal('0.0000'))
        igst_amount += item.get('igst_amount', Decimal('0.0000'))

    raw_grand_total = taxable_amount + cgst_amount + sgst_amount + igst_amount
    grand_total = raw_grand_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    round_off = Decimal('0.00')

    return {
        'subtotal': subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'taxable_amount': taxable_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'cgst_amount': cgst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'sgst_amount': sgst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'igst_amount': igst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'round_off': round_off,
        'grand_total': grand_total
    }
