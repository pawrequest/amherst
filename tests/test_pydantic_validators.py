from pycommence import pycommence_context

from amherst.models.amherst_models import AmherstCustomer, CSV_SEPERATOR, AmherstHire


def test_auto_csv(amherst_customer):
    ...
    tracks = amherst_customer.tracking_links_in
    print('\n RESULTS', tracks)
    assert isinstance(tracks, list)
    assert len(tracks) == 0


def test_it():
    cust = AmherstCustomer
    afield = cust.model_fields['name'].alias
    ...


def test_sep():
    pk = 'TEST RECORD DO NOT EDIT'
    new_tracking_links = ['Link4', 'Link5', 'Link6']
    new_tracking_numbers = ['Num4', 'Num5', 'Num6']
    with pycommence_context('Hire') as pyc:
        row = pyc.read_row(pk=pk)
        record = AmherstHire(**row.data, row_info=row.row_info)
        nums_field = record.alias_lookup('tracking_numbers')
        tracking_numbers = record.tracking_numbers
        tracking_numbers.extend(new_tracking_numbers)

        links_field = record.alias_lookup('tracking_links_out')
        old_links = record.tracking_links_out
        old_links.extend(new_tracking_links)

        update_package = {
            links_field: CSV_SEPERATOR.join(old_links),
            nums_field: CSV_SEPERATOR.join(tracking_numbers),
        }

        pyc.update_row(pk=pk, update_pkg=update_package)
