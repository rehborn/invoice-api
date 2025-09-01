import io
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from babel.dates import format_date
from babel.numbers import format_currency
from babel.support import Translations
from fastapi import FastAPI, Request, Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

import utils
from schema import *

__version__ = '0.0.1'

BASE_DIR = Path(__file__).resolve().parent.parent

STRF_DATE = "%Y-%m-%d"

fastapi_options = {
    # 'lifespan': lifespan,
    'title': 'PasteBox API',
    'description': "Simple Paste API",
    'version': __version__,
    'license_info': {
        'name': 'Apache 2.0',
        'url': 'https://www.apache.org/licenses/LICENSE-2.0.html',
    },
    'docs_url': None,
    'redoc_url': None,
    'openapi_url': None,
}

app = FastAPI(**fastapi_options)


@app.get('/', status_code=200, include_in_schema=False)
async def root(request: Request):
    data = yaml.safe_load(open(BASE_DIR / 'example-invoice.yaml', 'r').read())
    return data


def slugify(value):
    return value.lower().replace(' ', '-')


@app.post('/', status_code=200)
async def create_invoice(request: Request, payload: Invoice):
    context = payload.__dict__

    # dates
    if payload.created_date:
        created_date = datetime.strptime(payload.created_date, STRF_DATE)
    else:
        created_date = datetime.now()

    context['created_date'] = format_date(created_date, locale=payload.language)

    if payload.due_date:
        context['due_date'] = format_date(datetime.strptime(payload.due_date, STRF_DATE), locale=payload.language)
    else:
        context['due_date'] = format_date(created_date + timedelta(days=30), locale=payload.language)

    # invoice id
    if not context['invoice_id']:
        _company = slugify(payload.company.name)
        _customer = slugify(payload.customer.name)
        _date = created_date.strftime("%Y%m%d")
        context['invoice_id'] = f'{_company}-{_customer}-{_date}'

    fc = lambda x: format_currency(x, currency=payload.currency, locale=payload.language)

    # positions
    context['subtotal'] = 0
    positions = []
    for pos in payload.positions:
        rate = pos.rate if pos.rate else payload.hourly_rate
        amount = pos.amount if pos.amount else pos.quantity * rate
        positions.append({
            'description': pos.description,
            'quantity': pos.quantity,
            'rate': rate,
            'rate_formatted': fc(rate),
            'amount': amount,
            'amount_formatted': fc(amount),
        })
        context['subtotal'] += amount
    context['positions'] = positions

    # totals
    context['taxed'] = (context['subtotal'] / 100) * context['tax']
    context['total_with_tax'] = context['subtotal'] + context['taxed']

    # locale formatted
    context['taxed_formatted'] = fc(context['taxed'])
    context['total_with_tax_formatted'] = fc(context['total_with_tax'])
    context['subtotal_formatted'] = fc(context['subtotal'])

    # EPC QR Code
    context['sepa_qrcode'] = utils.sepa_qrcode(
        payload.company.name,
        payload.company.iban,
        payload.company.bic,
        str(context['total_with_tax']),
        context['invoice_id'],
        # payload.color,
    )
    # context['web_qrcode'] = utils.base64_qrcode(payload.company.web)

    # jinja and babel
    jinja_env = Environment(loader=FileSystemLoader(BASE_DIR / 'templates/'), extensions=['jinja2.ext.i18n'])
    # jinja_env.add_extension('jinja2.ext.debug')
    translations = Translations.load(BASE_DIR / 'locale', payload.language)
    jinja_env.install_gettext_translations(translations)

    jinja_template = jinja_env.get_template(f'{payload.template}.html')

    # render template
    html = jinja_template.render(invoice=context)
    easyprint = HTML(string=html).render()

    # attach xml

    # write pdf to buffer
    buffer = io.BytesIO()
    easyprint.write_pdf(buffer, pdf_variant="pdf/a-3b")
    buffer.seek(0)

    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(buffer.getvalue(), headers=headers, media_type='application/pdf')
