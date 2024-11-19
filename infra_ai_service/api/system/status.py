from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def status():
    return Response(content="", media_type="application/json")
