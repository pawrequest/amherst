from .. import sample_data
from .booking_route import router as booking_router
from .forms import router as forms_router
from .hire_route import router as hire_router
from .main_r import router as main_router

__all__ = ['hire_router', 'booking_router', 'sample_data', 'forms_router', 'main_router']
