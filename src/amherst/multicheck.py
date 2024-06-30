# import functools
# import time
# from collections.abc import Generator
# from datetime import date, timedelta
#
# import pandas as pd
# import matplotlib.dates as mdates
# import matplotlib.pyplot as plt
# from pawlogger import get_loguru
#
# from amherst.commence import HireFields, HireStatus
# from pycommence.pycmc_types import CmcDateFormat, CmcFilter, ConditionType, FilterArray, RadioType, to_cmc_date
# from pycommence.pycommence_v2 import PyCommence
#
# logger = get_loguru(profile='local')
#
#
# def daterang_gen(start_date, end_date) -> Generator[date, None, None]:
#     for x in range((end_date - start_date).days + 1):
#         thisdate = start_date + timedelta(days=x)
#         yield thisdate
#
#
# class Multi:
#     def __init__(
#             self, pycmc=None,
#             start_date: date = date.today(), end_date: date = date.today() + timedelta(days=6)
#     ):
#         self.start_date = start_date
#         self.end_date = end_date
#         self.date_range_gen = daterang_gen(start_date, end_date)
#         self.pycommence = pycmc or PyCommence.with_csr('Hire', filter_array=self.filters)
#         self.data = self._prepare_data()
#
#     def _prepare_data(self):
#         records = self.pycommence.records()
#         df = pd.DataFrame(records)
#         df[HireFields.SEND_OUT_DATE] = pd.to_datetime(
#             df[HireFields.SEND_OUT_DATE],
#             format=CmcDateFormat,
#             errors='coerce'
#         )
#         df[HireFields.DUE_BACK_DATE] = pd.to_datetime(
#             df[HireFields.DUE_BACK_DATE],
#             format=CmcDateFormat,
#             errors='coerce'
#         )
#         df[HireFields.UHF] = df[HireFields.UHF].astype(int)
#         return df
#
#     @property
#     def filters(self):
#         return FilterArray.from_filters(
#             CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
#             CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
#             CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
#             CmcFilter(
#                 cmc_col=HireFields.SEND_OUT_DATE,
#                 condition=ConditionType.BEFORE,
#                 value=to_cmc_date(self.end_date)
#             ),
#             CmcFilter(
#                 cmc_col=HireFields.SEND_OUT_DATE,
#                 condition=ConditionType.AFTER,
#                 value=to_cmc_date(self.start_date)
#             ),
#         )
#
#     def run(self):
#         ...
#
#
#
#
#
#
# if __name__ == '__main__':
#     starttime = time.perf_counter()
#     sc = Multi(
#         start_date=date(2023, 4, 1),
#         end_date=date(2023, 7, 1),
#     )
#     sc.run()
#     endtime = time.perf_counter()
#     print(f'THERE WERE {len(sc.data)} RECORDS')
#     print(f'Elapsed time: {endtime - starttime}')


