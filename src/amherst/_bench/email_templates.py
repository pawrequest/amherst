from __future__ import annotations

from amherst.front import support
from amherst.front.support import shipment_notification_labels_str
from amherst.models import shipment_record
from pawdantic import paw_strings
from shipaw.ship_ui import states
from suppawt.office_ps import email_handler as eh

from amherst.models.shipment_record import ShipmentRecordInDB


# def state_notification_labels_str(shipment: states.ShipState):
#     ret_str = ''
#     for notification in shipment.contact.notifications.notification_type:
#         ret_str += f'{pf_shared.notification_label_map[notification]} - {state_notification_contact_detail(shipment, notification)}\n'
#     return ret_str


def return_label_email(state):
    return eh.EmailMultipleAttachments(
        to_address=state.contact.email_address,
        subject='Radio Hire - Parcelforce Collection Label Attached',
        body=return_body(state),
        attachment_paths=[state.booking_state.label_dl_path],
    )


async def invoice_email(shiprec: ShipmentRecordInDB) -> eh.Email:
    inv_num = shiprec.record.invoice.stem
    return eh.Email(
        to_address=shiprec.shipment.contact.email_address,
        subject=f'Radio Hire - Invoice {inv_num} Attached',
        body=invoice_body(),
        attachment_path=shiprec.record.invoice,
    )


def invoice_body():
    return """
    Hi,
    
    Please find attached the invoice for your recent hire from Amherst.
    
    If you have any queries please let us know.
    
    Kind Regards
    Amherst Enterprises
    """


def return_body(state: states.Shipment):
    return f"""Hi,
    
    Thanks for choosing to hire from Amherst, please find a pre-paid parcelforce label attached – it needs to be printed and attached to the box.
    
    Please ensure any old postage labels are removed or thoroughly obscured as otherwise the parcel may be delivered back to you instead of coming home!
    
    Collection is booked for {paw_strings.date_string(state.ship_date)}, we are unable to give precise timings, however you should receive notifications at the contact details below:
        
{shipment_notification_labels_str(state)}
    
    If for any reason the courier is missed you can drop the labelled box at any uk postoffice.
    
    Any issues please let us know
    
    Kind Regards
    Amherst Enterprises
    """
