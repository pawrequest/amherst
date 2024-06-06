from amherst.front.book2 import router as booking_router
from amherst.front.booked2 import router as booked_router
from amherst.front.forms import router as forms_router
from amherst.front.emailer import router as email_router
from amherst.front.ship import router as shipping_router
from amherst.front.shared import router as shared_router

__all__ = [
    'shared_router',
    'booked_router',
    'booking_router',
    'forms_router',
    'shipping_router',
    'email_router',
]
