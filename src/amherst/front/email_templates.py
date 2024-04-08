from __future__ import annotations

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
