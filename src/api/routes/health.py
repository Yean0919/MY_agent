"""健康检查路由"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, str]:
    """健康检查"""
    return {"status": "healthy"}
