from amherst.front.book import router as booking_router
from amherst.front.booked import router as booked_router
from amherst.front.forms import router as forms_router
from amherst.front.forms_test import router as forms_test_router
from amherst.front.generic_emailer import router as email_router
from amherst.front.ship import router as shipping_router
from amherst.front.ship_model import router as ship_model_router
from amherst.front.splash import router as splash_router

__all__ = [
    'booked_router',
    'booking_router',
    'forms_router',
    'shipping_router',
    'splash_router',
    'ship_model_router',
    'forms_test_router',
    'email_router',
]
