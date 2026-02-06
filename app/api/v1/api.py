"""API v1 router configuration.

This module sets up the main API router and includes all sub-routers for different
endpoints like authentication and chatbot functionality.
"""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    ROOT_DIR_NAME = "klee-graph"
    script_path = Path(__file__).resolve()
    current_dir = script_path.parent
    project_root = None
    while True:
        if current_dir.name == ROOT_DIR_NAME:
            project_root = current_dir
            sys.path.insert(0, str(project_root))
            break
        current_dir = current_dir.parent
# --------------------------

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chatbot import router as chatbot_router
from app.core.logging import logger



api_router = APIRouter()

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])


@api_router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Health status information.
    """
    logger.info("health_check_called")
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":


    # 自检代码：验证路由配置是否正确
    print("=" * 50)
    print("API v1 Router 自检")
    print("=" * 50)

    # 检查路由器是否正确初始化
    print(f"\n✓ 主路由器类型: {type(api_router).__name__}")

    # 列出所有注册的路由
    print("\n已注册的路由:")
    for route in api_router.routes:
        methods = getattr(route, "methods", {"N/A"})
        path = getattr(route, "path", "N/A")
        name = getattr(route, "name", "N/A")
        print(f"  [{', '.join(methods)}] {path} -> {name}")

    # 检查子路由器
    print("\n已包含的子路由器:")
    print(f"  - auth_router: prefix=/auth, tags=['auth']")
    print(f"  - chatbot_router: prefix=/chatbot, tags=['chatbot']")

    # 测试健康检查函数（同步调用异步函数）
    import asyncio

    print("\n测试 health_check 端点:")
    result = asyncio.run(health_check())
    print(f"  返回值: {result}")

    if result.get("status") == "healthy":
        print("\n✓ 自检通过！")
    else:
        print("\n✗ 自检失败！")

    print("=" * 50)
