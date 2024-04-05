from .book import router as booking_router
from .booked import router as booked_router
from .forms import router as forms_router
from .forms_test import router as forms_test_router
from .ship import router as shipping_router
from .ship_model import router as ship_model_router
from .splash import router as splash_router

__all__ = [
    'booked_router',
    'booking_router',
    'forms_router',
    'shipping_router',
    'splash_router',
    'ship_model_router',
    'forms_test_router'

]
