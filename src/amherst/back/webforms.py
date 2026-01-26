from fastapi import APIRouter, FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from amherst.webforms.returns_auth import RMA

# router = APIRouter()
app = FastAPI()
TEMPLATES = Jinja2Templates(directory=r'C:\prdev\amdev\amherst\src\amherst\ui\templates')
app.mount('/static', StaticFiles(directory=r'C:\prdev\amdev\amherst\src\amherst\ui\static'), name='static')


@app.get('/rma')
def rma_form(request: Request):
    return TEMPLATES.TemplateResponse(request, 'rma.html')


@app.post('/rma_submit')
async def rma_submit(rma: RMA):
    # Process the RMA submission
    # For now, just return the received data
    ...
    return {
        "status": "success",
        "message": "RMA received",
        "rma_id": f"RMA-{id(rma)}",  # Placeholder ID
        "data": rma.model_dump()
    }
