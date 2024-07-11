from __future__ import annotations

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale
from amherst.models.commence_adaptors import CustomerAliases, HireAliases, SaleAliases

CURSOR_MAP = {
    'Hire': {
        'input_type': AmherstHire,
        'aliases': HireAliases,
        'template': 'orders.html',
    },
    'Sale': {
        'input_type': AmherstSale,
        'aliases': SaleAliases,
        'template': 'orders.html',
    },
    'Customer': {
        'input_type': AmherstCustomer,
        'aliases': CustomerAliases,
        'template': 'customers.html',
    },
}
