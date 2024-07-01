from __future__ import annotations

# from amherst.models import db_models
# from amherst.models.am_record import AmherstRecord, AmherstRecordIn


# def split_reference_numbers(record: AmherstRecord):
#     customer_str = record.customer
#     reference_numbers = {}
# 
#     for i in range(1, 6):
#         start_index = (i - 1) * 24
#         end_index = i * 24
#         if start_index < len(customer_str):
#             reference_numbers[f'reference_number{i}'] = customer_str[start_index:end_index]
#         else:
#             break
#     return reference_numbers


def split_refs_from_str(customer_str: str) -> dict[str, str]:
    reference_numbers = {}

    for i in range(1, 6):
        start_index = (i - 1) * 24
        end_index = i * 24
        if start_index < len(customer_str):
            reference_numbers[f'reference_number{i}'] = customer_str[start_index:end_index]
        else:
            break
    return reference_numbers


# def amherst_shipment_request(
#         record: AmherstRecord,
#         address: AddTypes,
# ) -> Shipment:
#     return Shipment(
#         recipient_contact=record.contact(),
#         recipient_address=address,
#         shipping_date=record.send_date,
#         total_number_of_parcels=record.boxes,
#         shipment_type=ShipmentType.DELIVERY,
#         **split_reference_numbers(record),
#     )


# async def amrec_to_booking(amrec: AmherstRecord):
#     booking = db_models.BookingStateDB(
#         record=amrec,
#         shipment_request=(
#             Shipment(
#                 recipient_contact=amrec.contact(),
#                 recipient_address=amrec.address_choice.address,
#                 shipping_date=amrec.send_date,
#                 total_number_of_parcels=amrec.boxes,
#                 shipment_type=ShipmentType.DELIVERY,
#                 **split_reference_numbers(amrec),
#             )
#         ),
#         # alerts=Alerts(alert=[Alert(code=None, message='Created')])
#     )
#     return booking


# async def cmc_record_to_amrec(record, el_client: ELClient | None = None) -> AmherstRecord:
#     el_client = el_client or ELClient(strict=False)
#     amrec_in = AmherstRecordIn.model_validate(record)
#     try:
#         amrec_in.address_choice = el_client.address_choice(amrec_in.input_address)
#     except:
#         amrec_in.address_choice = AddressChoice(address=amrec_in.input_address, score=0)
#     amrec = AmherstRecord.model_validate(amrec_in, from_attributes=True)
#     return amrec


def split_addr_str(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    used_lines = [_ for _ in addr_lines if _]
    town = used_lines.pop() if len(used_lines) > 1 else ''
    return {f'address_line{num}': line for num, line in enumerate(used_lines, start=1)} | {'town': town}
