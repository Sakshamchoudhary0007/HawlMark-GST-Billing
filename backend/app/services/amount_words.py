from decimal import Decimal
from num2words import num2words

def amount_to_words(amount: Decimal) -> str:
    # Convert amount (Decimal) to English words in Indian Rupee format.
    # Split into rupees (integer part) and paise (fractional part * 100).
    amount = amount.quantize(Decimal('0.01'))
    
    rupees = int(amount)
    paise = int((amount - Decimal(rupees)) * 100)
    
    rupees_words = num2words(rupees, lang='en_IN').title().replace(" And ", " and ")
    
    if paise > 0:
        paise_words = num2words(paise, lang='en_IN').title().replace(" And ", " and ")
        return f"Rupees {rupees_words} and {paise_words} Paise Only"
    else:
        return f"Rupees {rupees_words} Only"
