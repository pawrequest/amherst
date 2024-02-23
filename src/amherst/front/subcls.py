# from amherst.front import STYLESAm
# from amherst.models import Hire
# from amherst.models.shared import AddressAm
# from amherst.shipping.pfcom import choose_hire_address
# from shipr.el_combadge import get_postocde_addresses
# from pawsupport import fastui_ps as fuis
# from fastui import components as c
#
# from shipr import PFCom
#
#
# class AddressAmUi(AddressAm, fuis.Container):
#     class_name: str = STYLESAm.ADDRESS
#     @classmethod
#     def from_hire(cls, hire: Hire):
#         customer_txt = c.Text(text=hire.customer)
#         adrlines = hire.delivery_address.address.strip().splitlines()
#         addr_txts = [c.Text(text=_) for _ in adrlines]
#
#     @classmethod
#     async def hire_address(cls, hire: Hire, pfcom: PFCom):
#         candidates = pfcom.get_candidates(hire.delivery_address.postcode)
#         chosen_add, score = choose_hire_address(hire, candidates)
#
#         txts = all_text(hire.delivery_address)
#         am_address_col = Col.wrap(*txts, wrap_inner=Row)
#
#         txtsch = all_text(chosen_add)
#         chosen_add_col = Col.wrap(*txtsch, wrap_inner=Row)
#
#         buttons = [
#             c.Text(text=f'Address score: {score}'),
#             c.Button(text="Choose this address"),
#             c.Button(text="Enter address manually", on_click=None),
#         ]
#         btn_col = Col.wrap(*buttons, wrap_inner=Row)
#
#         cols = [am_address_col, btn_col, chosen_add_col]
#         row1 = Row(components=cols)
#
#         others = [all_text(_) for _ in candidates]
#         other_cols = [Col.wrap(*_, wrap_inner=Row) for _ in others]
#         others_row = Row(components=other_cols)
#
#         rows = [row1, others_row]
#
#         con = Container(components=rows)
#
#         page = Page.default_page(con, title="Address selection")
#         return page
#
