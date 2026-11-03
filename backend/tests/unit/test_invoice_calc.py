import pytest
from decimal import Decimal
from app.services.invoice_calc import calculate_line_item, calculate_invoice_summary
from app.services.amount_words import amount_to_words

def test_calculate_line_item_cgst_sgst():
    res = calculate_line_item(
        quantity=Decimal('10.00'),
        rate=Decimal('100.00'),
        discount_amount=Decimal('50.00'),
        gst_rate=Decimal('18.00'),
        tax_mode='CGST_SGST'
    )
    assert res['subtotal'] == Decimal('1000.00')
    assert res['taxable_amount'] == Decimal('950.00')
    assert res['cgst_amount'] == Decimal('85.5000')
    assert res['sgst_amount'] == Decimal('85.5000')
    assert res['igst_amount'] == Decimal('0.0000')
    assert res['total_amount'] == Decimal('1121.0000')

def test_calculate_line_item_igst():
    res = calculate_line_item(
        quantity=Decimal('5.00'),
        rate=Decimal('200.00'),
        discount_amount=Decimal('0.00'),
        gst_rate=Decimal('12.00'),
        tax_mode='IGST'
    )
    assert res['subtotal'] == Decimal('1000.00')
    assert res['taxable_amount'] == Decimal('1000.00')
    assert res['cgst_amount'] == Decimal('0.0000')
    assert res['sgst_amount'] == Decimal('0.0000')
    assert res['igst_amount'] == Decimal('120.0000')
    assert res['total_amount'] == Decimal('1120.0000')

def test_calculate_line_item_zero_values():
    res = calculate_line_item(
        quantity=Decimal('0.00'),
        rate=Decimal('0.00'),
        discount_amount=Decimal('0.00'),
        gst_rate=Decimal('18.00'),
        tax_mode='IGST'
    )
    assert res['total_amount'] == Decimal('0.0000')

def test_calculate_invoice_summary():
    items = [
        {
            'subtotal': Decimal('1000.00'),
            'taxable_amount': Decimal('950.00'),
            'cgst_amount': Decimal('85.5000'),
            'sgst_amount': Decimal('85.5000'),
            'igst_amount': Decimal('0.0000'),
            'total_amount': Decimal('1121.0000')
        },
        {
            'subtotal': Decimal('500.00'),
            'taxable_amount': Decimal('500.00'),
            'cgst_amount': Decimal('45.0000'),
            'sgst_amount': Decimal('45.0000'),
            'igst_amount': Decimal('0.0000'),
            'total_amount': Decimal('590.0000')
        }
    ]
    
    # Raw total = 950 + 500 + 85.50 + 45 + 85.50 + 45 = 1711.0000
    res = calculate_invoice_summary(items, 'CGST_SGST')
    assert res['subtotal'] == Decimal('1500.00')
    assert res['taxable_amount'] == Decimal('1450.00')
    assert res['cgst_amount'] == Decimal('130.50')
    assert res['sgst_amount'] == Decimal('130.50')
    assert res['igst_amount'] == Decimal('0.00')
    assert res['round_off'] == Decimal('0.00')
    assert res['grand_total'] == Decimal('1711.00')

def test_calculate_invoice_summary_exact_values():
    items = [
        {
            'subtotal': Decimal('100.00'),
            'taxable_amount': Decimal('100.00'),
            'cgst_amount': Decimal('9.1234'),
            'sgst_amount': Decimal('9.1234'),
            'igst_amount': Decimal('0.0000'),
            'total_amount': Decimal('118.2468')
        }
    ]
    # Raw total = 100 + 9.1234 + 9.1234 = 118.2468 -> 118.25
    res = calculate_invoice_summary(items, 'CGST_SGST')
    assert res['grand_total'] == Decimal('118.25')
    assert res['round_off'] == Decimal('0.00')

def test_amount_to_words_integer():
    assert amount_to_words(Decimal('1250.00')) == "Rupees One Thousand, Two Hundred and Fifty Only"

def test_amount_to_words_with_paise():
    assert amount_to_words(Decimal('1250.50')) == "Rupees One Thousand, Two Hundred and Fifty and Fifty Paise Only"
