from fastapi import APIRouter

router = APIRouter()


@router.get("/{path:path}", status_code=404)
async def api_404():
    return {"message": "Not Found"}
