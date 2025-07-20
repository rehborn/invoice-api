import os

import requests
import yaml
from pprint import pprint
from sys import argv

INVOICE_API = os.environ.get('INVOICE_API', 'http://localhost:8000')

if argv[1:]:
    source = argv[1]
else:
    source = 'example-invoice.yaml'

data = yaml.safe_load(open(source, 'r').read())
pprint(data)

r = requests.post(INVOICE_API, json=data)
if r.status_code >= 400:
    print(r.status_code)
    print(r.text)

destination = source.replace('.yaml', '.pdf')
with open(destination, 'wb') as pdf:
    pdf.write(r.content)
