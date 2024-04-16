from amherst.front.book import router as booking_router
from amherst.front.booked import router as booked_router
from amherst.front.forms import router as forms_router
from amherst.front.generic_emailer import router as email_router
from amherst.front.ship import router as shipping_router

__all__ = [
    'booked_router',
    'booking_router',
    'forms_router',
    'shipping_router',
    'email_router',
]
