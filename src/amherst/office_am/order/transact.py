# import json
# from typing import List
#
# import pandas as pd
# from office_tools.excel import df_overwrite_wb
# from suppawt.office_ps.o_tool import
#
# from .order_ent import FreeItem, HireInvoice, HireOrder, LineItem
# from ..dflt import DFLT_CONST, DFLT_PATHS, DTYPES, FIELDS
#
#
# def transaction_closure(prices_wb=DFLT_PATHS.PRC_WB, prcs_out=DFLT_PATHS.PRC_OUT, jsong_file=DFLT_PATHS.PRCS_JSON,
#                         header_row=DFLT_CONST.PRC_HEAD):
#     df_bands, df_pr_hire, df_pr_sale = get_dfs()
#
#
# def get_dfs():
#     # df_bands, df_hire, df_sale = dfs_from_json() if json_file.exists() else dfs_from_excel()
#     df_bands, df_hire, df_sale = dfs_from_excel()
#     return df_bands, df_hire, df_sale
#
#
# def dfs_from_excel(prcs_wb=DFLT_PATHS.PRC_WB):
#     hire = pd.read_excel(prcs_wb, sheet_name='Hire', header=0,
#                          dtype=DTYPES.HIRE_PRICES)
#     sale = pd.read_excel(prcs_wb, sheet_name='Sale', header=0,
#                          dtype=DTYPES.SALE_PRICES)
#     bands = pd.read_excel(prcs_wb, sheet_name='Bands', header=0,
#                           dtype=str)
#
#     return bands, hire, sale
#
#
# def dfs_from_json(json_file=DFLT_PATHS.PRCS_JSON):
#     with open(json_file, 'r') as json_file2:
#         data = json.load(json_file2)
#     bands = pd.DataFrame(data['df_b'], dtype=str)
#     hire = pd.DataFrame(data['df_hire']).astype(DTYPES.HIRE_PRICES, errors='ignore')
#     sale = pd.DataFrame(data['df_sale']).astype(DTYPES.SALE_PRICES, errors='ignore')
#
#     return bands, hire, sale
#
#
# def dfs_to_wb(df_pr_hire, df_pr_sale, df_bands):
#     # todo convert back from 100
#     df_overwrite_wb(input_workbook=DFLT_PATHS.PRC_WB, sheet='Hire', header_row=0,
#                     out_file=DFLT_PATHS.PRC_OUT, df=df_pr_hire)
#     df_overwrite_wb(input_workbook=DFLT_PATHS.PRC_WB, sheet='Sale', header_row=0,
#                     out_file=DFLT_PATHS.PRC_OUT, df=df_pr_sale)
#     df_overwrite_wb(input_workbook=DFLT_PATHS.PRC_WB, sheet='Bands', header_row=0,
#                     out_file=DFLT_PATHS.PRC_OUT, df=df_bands)
#
#
# def dfs_to_json(df_pr_hire, df_pr_sale, df_bands, json_file=DFLT_PATHS.PRCS_JSON):
#     data = {
#         'df_hire': df_pr_hire.astype(str).to_dict(),
#         'df_sale': df_pr_sale.astype(str).to_dict(),
#         'df_b': df_bands.astype(str).to_dict(),
#     }
#     ...
#     with open(json_file, 'w') as jfile:
#         json.dump(data, jfile, indent=4)
#
#
# class TransactionManager:
#     def __init__(self, df_bands: pd.DataFrame, df_hire: pd.DataFrame, df_sale: pd.DataFrame):
#         self.df_bands = df_bands
#         self.df_hire = df_hire
#         self.df_sale = df_sale
#
#     def get_hire_invoice(self, hire: dict) -> HireInvoice:
#         if 'Delivery Cost' not in hire or not hire['Delivery Cost']:
#             shipping = 0
#         else:
#             shipping = hire['Delivery Cost']
#
#         line_items = lines_from_hire(self.df_bands, self.df_hire, hire)
#         if not any([line_items[0], line_items[1]]):
#             raise ValueError(f"No line items found for hire {hire['Name']}")
#         hire_order = HireOrder(customer=hire['customer'], line_items=line_items[0], free_items=line_items[1],
#                                shipping=shipping,
#                                duration=hire['Weeks'])
#         return HireInvoice.from_hire(hire, hire_order)
#
#     # def sale_to_invoice(self, sale: pd.Series):
#     #     customer = cust_of_transaction(sale.Name, 'Sale')
#     #     line_items = lines_from_sale(self.df_bands, self.df_sale, sale)
#     #     order = Order(customer.Name, line_items)
#     #     invoice = SaleInvoice.from_sale(sale, order, customer)
#     #     invoice.generate()
#
#
# def hire_item_description(df_bands, df_hire, item_name: str):
#     desc = df_hire.loc[df_hire['Name'].str.lower() == item_name.lower(), 'Description']
#     if desc.empty:
#         desc = df_bands.loc[df_bands['Name'].str.lower() == item_name.lower(), 'Description']
#     if not desc.empty:
#         desc = desc.iloc[0]
#         return desc
#     return ""
#
#
# def get_hire_price(df_hire: pd.DataFrame, product_name: str, quantity: int, duration: int):
#     product = df_hire.loc[df_hire['Name'].str.lower() == str(product_name).lower()]
#     if product.empty:
#         prod_band = get_accessory_priceband(product_name)
#         if prod_band is None:
#             raise ValueError(f"No hire product or band found for {product_name}")
#         product = df_hire.loc[df_hire['Name'].str.lower() == prod_band.lower()]
#         if product.empty:
#             raise ValueError(f"No hire product or band found for {product_name}")
#
#     valid_products = product[
#         (product['Min Qty'] <= quantity) & (product['Min Duration'] <= int(duration))]
#
#     if valid_products.empty:
#         raise ValueError(f"No valid price for {product_name}")
#
#     best_product = valid_products.sort_values(by=['Min Qty', 'Min Duration'], ascending=[False, False]).iloc[0]
#     price = best_product['Price']
#     return price
#
#
# def get_sale_price(df_sale: pd.DataFrame, product_name: str, quantity: int):
#     product_df = df_sale.loc[df_sale['Name'].str.lower() == product_name.lower()]
#     return product_df.loc[product_df[DFLT_CONST.MIN_QTY].astype(int) <= int(quantity), 'Price'].min()
#
#
# def hire_lineitems_pay(df_h: pd.DataFrame, pay_items: dict, duration: int, df_bands: pd.DataFrame):
#     line_items = []
#     for name, qty in pay_items.items():
#         if not qty:
#             continue
#         description = hire_item_description(df_bands=df_bands, df_hire=df_h, item_name=name)
#         price = get_hire_price(df_hire=df_h, product_name=name, quantity=qty, duration=duration)
#         long_name = f'{name}_hire_{duration}_weeks'
#         line_items.append(LineItem(name=long_name, description=description, price_each=price, quantity=int(qty)))
#     return line_items
#
#
# def hire_lineitems_free(df_bands: pd.DataFrame, df_hire: pd.DataFrame, duration: int, free_items: dict) -> list:
#     line_items = []
#     for name, qty in free_items.items():
#         description = hire_item_description(df_bands, df_hire, name)
#         long_name = f'{name}_hire_{duration}_weeks'
#         line_items.append(FreeItem(name=long_name, description=description, quantity=qty))
#     return line_items
#
#
# def lines_from_hire(df_bands, df_hire, hire: dict) -> tuple[list, list]:
#     duration = hire['Weeks']
#     hire_itms = items_dict_from_hire(hire)
#     free = {k: v for k, v in hire_itms.items() if k in FIELDS.FREE_ITEMS}
#     pay = {k: v for k, v in hire_itms.items() if k not in FIELDS.FREE_ITEMS}
#     free_items = hire_lineitems_free(df_bands, df_hire, duration, free)
#     line_items = hire_lineitems_pay(df_h=df_hire, pay_items=pay, duration=duration, df_bands=df_bands)
#     return line_items, free_items
#
#
# def items_dict_from_hire(hire: dict) -> dict:
#     all_items = item_nams_from_hire(hire)
#     items_dict = {k[7:]: v for k, v in hire.items() if k in all_items}
#     return items_dict
#
#
# def item_nams_from_hire(hire: dict) -> List:
#     item_keys = [col for col in hire.keys() if col.startswith('Number ')]
#     return item_keys
#
#
# def get_accessory_priceband(accessory_name: str):
#     if accessory_name in ["EM", 'Parrot', 'Battery', 'Batteries', 'Cases']:
#         return "Accessory A"
#     elif accessory_name in ['EMC', 'Headset']:
#         return "Accessory B"
#     elif accessory_name in ['Aircraft', 'Headset Big']:
#         return "Aircraft"
#     elif accessory_name == 'Icom':
#         return 'Mobile'
#     else:
#         return None
#
#
# def items_from_sale(sale: pd.Series):
#     all_items = sale.loc['Items Ordered']
#     item_lines = all_items.split('\r\n')
#     item_tups = []
#     for line in item_lines:
#         res = line.split(' x ')
#         if len(res) != 2:
#             continue
#         item_name, qty = res
#         item_tups.append((item_name, int(qty)))
#     return item_tups
#
# class TransactionContext:
#     def __init__(self, header_row=None, out_file=None, prices_wb=None, ):
#         self.prcs_wb = prices_wb or DFLT_PATHS.PRC_WB
#         self.prcs_out = out_file or DFLT_PATHS.PRC_OUT
#         self.json_file = self.prcs_out.with_suffix('.json')  # JSON file path with new suffix
#         self.header_row = header_row or int(DFLT_CONST.PRC_HEAD)
#         self.df_bands, self.df_pr_hire, self.df_pr_sale = self.get_dfs()
#
#     def __enter__(self) -> TransactionManager:
#         self.transaction_manager = TransactionManager(df_bands=self.df_bands, df_hire=self.df_pr_hire,
#                                                       df_sale=self.df_pr_sale)
#         return self.transaction_manager
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         # if input("Save changes? (y/n)").lower() != 'y':
#         #     return
#         self.dfs_to_json()
#         # self.dfs_to_wb()
#
#     def get_dfs(self):
#         assert self.prcs_wb.exists()
#
#         # df_bands, df_hire, df_sale = self.dfs_from_json() if self.json_file.exists() else self.dfs_from_excel()
#         df_bands, df_hire, df_sale = self.dfs_from_excel()
#         return df_bands, df_hire, df_sale
#
#     def dfs_from_excel(self):
#         hire = pd.read_excel(self.prcs_wb, sheet_name='Hire', header=0,
#                              dtype=DTYPES.HIRE_PRICES)
#         sale = pd.read_excel(self.prcs_wb, sheet_name='Sale', header=0,
#                              dtype=DTYPES.SALE_PRICES)
#         bands = pd.read_excel(self.prcs_wb, sheet_name='Bands', header=0,
#                               dtype=str)
#
#         return bands, hire, sale
#
#     def dfs_from_json(self):
#         with open(self.json_file, 'r') as json_file2:
#             data = json.load(json_file2)
#         bands = pd.DataFrame(data['df_b'], dtype=str)
#         hire = pd.DataFrame(data['df_hire']).astype(DTYPES.HIRE_PRICES, errors='ignore')
#         sale = pd.DataFrame(data['df_sale']).astype(DTYPES.SALE_PRICES, errors='ignore')
#
#         return bands, hire, sale
#
#     def dfs_to_wb(self):
#         # todo convert back from 100
#         df_overwrite_wb(input_workbook=DFLT_PATHS.PRC_WB, sheet='Hire', header_row=0,
#                         out_file=DFLT_PATHS.PRC_OUT, df=self.df_pr_hire)
#         df_overwrite_wb(input_workbook=DFLT_PATHS.PRC_WB, sheet='Sale', header_row=0,
#                         out_file=DFLT_PATHS.PRC_OUT, df=self.df_pr_sale)
#         df_overwrite_wb(input_workbook=DFLT_PATHS.PRC_WB, sheet='Bands', header_row=0,
#                         out_file=DFLT_PATHS.PRC_OUT, df=self.df_bands)
#
#     def dfs_to_json(self):
#         data = {
#             'df_hire': self.df_pr_hire.astype(str).to_dict(),
#             'df_sale': self.df_pr_sale.astype(str).to_dict(),
#             'df_b': self.df_bands.astype(str).to_dict(),
#         }
#         ...
#         with open(self.json_file, 'w') as json_file:
#             json.dump(data, json_file, indent=4)
#
