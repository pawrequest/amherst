import pprint
from pathlib import Path

from loguru import logger
from pycommence import pycommence_context


def link_hire_invoice_row_id(row_id: str, invoice_file: Path):
    try:
        update_dict = {'Invoice': str(invoice_file)}
        logger.info(f'Updating CMC: {update_dict}')
        with pycommence_context(csrname='Hire') as pycmc1:
            pycmc1.update_row(update_dict, row_id=row_id)
        logger.info(f'Updated Commence Hire ({row_id=}) with:\n{pprint.pformat(update_dict, indent=2)}')

    except Exception as e:
        logger.exception(e)
        raise


def link_hire_invoice_pk(row_pk: str, invoice_file: Path):
    try:
        with pycommence_context(csrname='Hire') as pycmc:
            row_id = pycmc.csr().pk_to_id(row_pk)
        if not row_id:
            raise ValueError(f'No row found with PK {row_pk}')
        link_hire_invoice_row_id(row_id, invoice_file)
    except Exception as e:
        logger.exception(e)
        raise


if __name__ == '__main__':
    link_hire_invoice_pk('TEST RECORD DO NOT EDIT', Path(r'C:\prdev\wordmacro\dest\A26424.docx'))
    