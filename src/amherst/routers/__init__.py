from .hire_route import router as hire_router
from .booking_route import router as booking_router
from .main_route import router as main_router
from .test_rout import router as rout
from .server_load import router as server_load_router
from .forms import router as forms_router
from .. import sample_data

__all__ = ["hire_router", "booking_router", "rout", "main_router", "server_load_router", "sample_data", 'forms_router']
