from __future__ import annotations

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale
from amherst.models.commence_adaptors import CustomerAliases, HireAliases, SaleAliases
from amherst.models.filters import cust_init_2, hire_fils_initial_array, sale_fils_initial_array

CURSOR_MAP = {
    'Hire': {
        'input_type': AmherstHire,
        'aliases': HireAliases,
        'template': 'orders.html',
        'initial_filter': hire_fils_initial_array(),
    },
    'Sale': {
        'input_type': AmherstSale,
        'aliases': SaleAliases,
        'template': 'orders.html',
        'initial_filter': sale_fils_initial_array(),

    },
    'Customer': {
        'input_type': AmherstCustomer,
        'aliases': CustomerAliases,
        'template': 'customers.html',
        'initial_filter': cust_init_2(),
    },
}

FILTER_MAP = {
    'initial_hire': hire_fils_initial_array(),
    'initial_sale': sale_fils_initial_array(),
    'initial_customer': cust_init_2(),
}
