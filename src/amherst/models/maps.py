from __future__ import annotations

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale
from amherst.models.commence_adaptors import CustomerAliases, HireAliases, SaleAliases

CURSOR_MAP = {
    'Hire': {
        'input_type': AmherstHire,
        'aliases': HireAliases,
        'template': 'order.html',
    },
    'Sale': {
        'input_type': AmherstSale,
        'aliases': SaleAliases,
        'template': 'order.html',
    },
    'Customer': {
        'input_type': AmherstCustomer,
        'aliases': CustomerAliases,
        'template': 'customer.html',
    },
}
