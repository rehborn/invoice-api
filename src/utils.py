import io
from base64 import b64encode
from typing import Optional

import segno


def base64_qrcode(text: str, **kwargs) -> str:
    buffer = io.BytesIO()
    segno.make(text, error='l').save(buffer, kind='svg', border=0, **kwargs)
    return "data:image/svg+xml;base64,{}==".format(b64encode(buffer.getvalue()).decode())


def sepa_qrcode(name: str, iban: str, bic: str, amount: str, invoice_id: str, color: Optional[str] = 'black') -> str:
    """
    https://en.wikipedia.org/wiki/EPC_QR_code
    """
    text = [
        'BCD',
        '001',
        '1', # utf-8
        'SCT', # SEPA Credit Transfer
        bic,  # BIC
        name,  # Name
        iban.replace(' ', ''),  # IBAN
        'EUR' + amount,  # Amount
        '', # optional reason max 4 chars
        invoice_id, # Ref of invoice - max 35 chars
        '', # optional description - max 140 chars
        '' # optional note - max 70 chars
    ]
    return base64_qrcode('\n'.join(text), dark=color, data_dark='black', data_light='white')
