from .. import sample_data
from .booking_route import router as booking_router
from .forms import router as forms_router
from .main_r import router as main_router
from .shipping_route import router as ship_router
from .server_load import router as server_router

__all__ = ['ship_router', 'booking_router', 'sample_data', 'forms_router', 'main_router', 'server_router']
