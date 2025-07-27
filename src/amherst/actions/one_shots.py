from pathlib import Path
from pprint import pprint

from amherst.set_env import set_amherstpr_env

set_amherstpr_env(sandbox=False)

from amherst.models.commence_adaptors import HireStatus
from amherst.models.commence_aliases import CustomerAliases, HireAliases
from pycommence.filters import ConditionType, FieldFilter, FilterArray
from pycommence.pycommence import PyCommence

# from datetime import date, timedelta
#
# import matplotlib.pyplot as plt
#
# from amherst.commence import HireFields, HireStatus
# from pycommence import FilterArray, PyCommence
# from pycommence.pycmc_types import CmcFilter, ConditionType, RadioType
# from shipaw.expresslink_client importELClient
# from shipaw.pf_config import PFSettings
#
#
from shipaw.expresslink_client import ELClient
from shipaw.pf_config import PFSettings

from amherst.set_env import set_amherstpr_env


def expresslink_live() -> ELClient:
    return ELClient(
        settings=PFSettings(
            _env_file=r'R:\paul_r\.internal\envs\pf_live.env',
        ),
    )


def get_a_label(dl_path, shipment_number):
    return


def good_hires_fils():
    return (
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
    )


def good_hires_array():
    return FilterArray(filters={i: fil for i, fil in enumerate(good_hires_fils(), 1)})


def cust_array():
    return FilterArray(
        filters={
            1: FieldFilter(column=CustomerAliases.DATE_LAST_CONTACTED, condition=ConditionType.AFTER, value='2022'),
        }
    )


def pyc_test():
    pyc2 = PyCommence.with_csr('Hire')
    pyc2.filter_cursor(good_hires_array(), 'Hire')
    assert pyc2.csrs['Hire'].row_count > 0
    pyc2.set_csr('Customer')
    pyc2.filter_cursor(cust_array(), 'Customer')
    assert pyc2.csrs['Customer'].row_count > 0


# pyc_test()


def pf_play(el_client):
    candidates = el_client.get_candidates('SG8 5HW')
    return candidates


if __name__ == '__main__':
    dl_path = Path(r'C:\prdev\myfile.pdf')
    ship_nuim = 'XG0442462'
    el_client = expresslink_live()
    # res = pf_play(el_client)
    res = el_client.get_label(ship_nuim, str(dl_path))
    pprint(res)
    ...

    # print(el_client.get_candidates('PE25 2QH'))


# # def rads_out_filter(datecheck: date):
# #     hires_fil = good_hires_array()
# #     hires_fil.filters[4] = CmcFilter(
# #
# #
# #     # return FilterArray(
# #     #     filters={
# #     #         1: CmcFilter(cmc_col=HireFields.STATUS, condition='Equal To', value=HireStatus.BOOKED_IN),
# #     #         1: CmcFilter(cmc_col=HireFields.STATUS, not_flag='Not', condition='Equal To', value=HireStatus.CANCELLED),
# #     #         2: CmcFilter(cmc_col=HireFields.STATUS, not_flag='Not', condition='Equal To', value=HireStatus.RTN_OK),
# #     #         3: CmcFilter(
# #     #             cmc_col=HireFields.STATUS, not_flag='Not', condition='Equal To', value=HireStatus.RTN_PROBLEMS
# #     #         ),
# #     #         **good_hires_fils(),
# #             4: CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition='Before', value=datecheck.isoformat()),
# #             5: CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition='After', value=datecheck.isoformat()),
# #         }
# #     )
#
#
# def good_hires_fils():
#     return [
#         CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
#         CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
#         CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
#     ]
#
#
# def good_hires_array():
#     return FilterArray(
#         filters={
#             1: CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
#             2: CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
#             3: CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
#         }
#     )
#
#
# def hires_out_array(datecheck: date, radiotype=RadioType.HYT):
#     hires_fil = good_hires_array()
#     hires_fil.filters[4] = CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition='Before', value=datecheck.isoformat())
#     hires_fil.filters[5] = CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition='After', value=datecheck.isoformat())
#     hires_fil.filters[6] = CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition='Equal To', value=radiotype)
#     return hires_fil
#
#
# def hires_out_fils(datecheck: date, radiotype=RadioType.HYT):
#     return (
#         CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition='Before', value=datecheck.isoformat()),
#         CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition='After', value=datecheck.isoformat()),
#         CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition='Equal To', value=radiotype),
#     )
#
#
# def send_on_date_array(datecheck: date, radiotype=RadioType.HYT):
#     return FilterArray(
#         filters={
#             1: CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition=ConditionType.EQUAL, value=datecheck.isoformat()),
#             2: CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition=ConditionType.EQUAL, value=radiotype),
#         }
#     )
#
#
# def send_on_date_fils(datecheck: date, radiotype=RadioType.HYT):
#     return (
#         CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition=ConditionType.EQUAL, value=datecheck.isoformat()),
#         CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition=ConditionType.EQUAL, value=radiotype),
#     )
#
#
# def how_many(datecheck: date):
#     out_filter = hires_out_array(datecheck)
#     recs = get_records(out_filter)
#     rads_out = sum([int(rec.get(HireFields.UHF)) for rec in recs])
#     return rads_out
#
#
# def to_send(datecheck: date):
#     to_send_fil = send_on_date_fil(datecheck)
#     recs = get_records(to_send_fil)
#     return sum([int(rec.get(HireFields.UHF)) for rec in recs])
#
#
# def get_records(to_send_fil):
#     with PyCommence.from_table_name_context('Hire', filter_array=to_send_fil) as pyc:
#         recs = pyc.records()
#     return recs
#
#
# def do_matplot(start_date: date, end_date: date):
#     data = get_data(start_date, end_date)
#
#     dates = [d[0] for d in data]
#     radios_out = [d[1] for d in data]
#
#     # Plotting the data
#     plt.figure(figsize=(14, 7))
#     plt.plot(dates, radios_out, label='Radios Out')
#     plt.axhline(y=750, color='r', linestyle='--', label='Stock Limit (750)')
#     plt.xlabel('Date')
#     plt.ylabel('Number of Radios Out')
#     plt.title('Radio Stock Tracker')
#     plt.legend()
#     plt.grid(True)
#     plt.show()
#
#
# def get_data(start_date, end_date):
#     date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
#     data = []
#     for datecheck in date_range:
#         print(f'{to_send(datecheck)} radios to send on {datecheck.isoformat()}')
#         rads_out = how_many(datecheck)
#         print(f'Radios out on {datecheck.isoformat()} : {rads_out}')
#         data.append((datecheck, rads_out))
#     return data
#
#
# if __name__ == '__main__':
#     do_matplot(date.today(), date.today() + timedelta(days=3))
#     # do_how_many()
#     # print(el_client.get_candidates('PE25 2QH'))

