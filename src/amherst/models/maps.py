from __future__ import annotations

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale
from amherst.models.commence_adaptors import CustomerAliases, HireAliases, SaleAliases
from amherst.models.filters import CUSTOMER_FILTER_ARRAY, HIRE_FILTER_ARRAY, SALE_FILTER_ARRAY

CURSOR_MAP = {
    'Hire': {
        'input_type': AmherstHire,
        'aliases': HireAliases,
        'template': 'orders.html',
        'filters': {
            'initial': HIRE_FILTER_ARRAY,
        }
    },
    'Sale': {
        'input_type': AmherstSale,
        'aliases': SaleAliases,
        'template': 'orders.html',
        'filters': {
            'initial': SALE_FILTER_ARRAY,
        }
    },
    'Customer': {
        'input_type': AmherstCustomer,
        'aliases': CustomerAliases,
        'template': 'customers.html',
        'filters': {
            'initial': CUSTOMER_FILTER_ARRAY,
        }
    },
}

