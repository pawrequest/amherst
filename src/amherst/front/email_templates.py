from __future__ import annotations

from amherst.front import support
from amherst.models import managers
from pawdantic import paw_strings
from shipr.models import pf_shared
from shipr.ship_ui import states
from suppawt.office_ps.email_handler import Email


def state_notification_labels_str(state: states.ShipState):
    indent = ' ' * 4
    lines = [
        f'{indent}{pf_shared.notification_label_map[notification]} - {state_notification_contact_detail(state, notification)}'
        for notification in state.contact.notifications.notification_type
    ]
    return '\n'.join(lines)


# def state_notification_labels_str(state: states.ShipState):
#     ret_str = ''
#     for notification in state.contact.notifications.notification_type:
#         ret_str += f'{pf_shared.notification_label_map[notification]} - {state_notification_contact_detail(state, notification)}\n'
#     return ret_str


def state_notification_contact_detail(state: states.ShipState, notification: str):
    if 'EMAIL' in notification or notification == 'DELIVERYNOTIFICATION':
        return state.contact.email_address
    elif 'SMS' in notification:
        return state.contact.mobile_phone
    else:
        raise ValueError('Invalid notification type')


def return_label_email(state):
    return Email(
        to_address=state.contact.email_address,
        subject='Radio Hire - Parcelforce Collection Label Attached',
        body=return_body(state),
        attachment_path=state.booking_state.label_dl_path,
    )


async def invoice_email(manager: managers.MANAGER_IN_DB) -> Email:
    inv_file = await support.get_invoice_path(manager)
    inv_num = inv_file.split('\\')[-1].split('.')[0]
    return Email(
        to_address=manager.state.contact.email_address,
        subject=f'Radio Hire - Invoice {inv_num} Attached',
        body=invoice_body(),
        attachment_path=inv_file,
    )


def invoice_body():
    return """
    Hi,
    
    Please find attached the invoice for your recent hire from Amherst.
    
    If you have any queries please let us know.
    
    Kind Regards
    Amherst Enterprises
    """


def return_body(state: states.ShipState):
    return f"""Hi,
    
    Thanks for choosing to hire from Amherst, please find a pre-paid parcelforce label attached – it needs to be printed and attached to the box.
    
    Please ensure any old postage labels are removed or thoroughly obscured as otherwise the parcel may be delivered back to you instead of coming home!
    
    Collection is booked for {paw_strings.date_string(state.ship_date)}, we are unable to give precise timings, however you should receive notifications at the contact details below:
        
{state_notification_labels_str(state)}
    
    If for any reason the courier is missed you can drop the labelled box at any uk postoffice.
    
    Any issues please let us know
    
    Kind Regards
    Amherst Enterprises
    """
