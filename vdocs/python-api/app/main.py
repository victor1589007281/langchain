"""LangChain RESTful API Service - 主应用

基于 FastAPI 构建的 LangChain 服务，提供完整的 LangChain 功能。
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from app.api import chat, rag, agent, embeddings, tools, chains
from app.core.config import settings
from app.core.logging_config import setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger.info("🚀 LangChain API Service 启动中...")
    logger.info(f"📝 环境: {settings.ENVIRONMENT}")
    logger.info(f"🔧 调试模式: {settings.DEBUG}")

    # 启动时的初始化操作
    yield

    # 关闭时的清理操作
    logger.info("👋 LangChain API Service 关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## LangChain RESTful API Service

    提供完整的 LangChain 功能，包括：

    * **💬 Chat API** - 对话和聊天功能
    * **📚 RAG API** - 检索增强生成
    * **🤖 Agent API** - 智能代理
    * **🔢 Embeddings API** - 文本向量化
    * **🛠️ Tools API** - 工具管理和调用
    * **⛓️ Chains API** - 链式操作

    ### 快速开始

    1. 配置环境变量（特别是 API Keys）
    2. 选择合适的端点
    3. 发送 POST 请求

    ### 认证

    使用 `X-API-Key` header 进行认证（如果启用）
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["系统"])
async def root():
    """根端点 - API 信息"""
    return {
        "message": "🦜 LangChain RESTful API Service",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/api/v1/chat",
            "rag": "/api/v1/rag",
            "agent": "/api/v1/agent",
            "embeddings": "/api/v1/embeddings",
            "tools": "/api/v1/tools",
            "chains": "/api/v1/chains"
        }
    }


# 注册路由
app.include_router(chat.router, prefix="/api/v1/chat", tags=["💬 Chat"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["📚 RAG"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["🤖 Agent"])
app.include_router(embeddings.router, prefix="/api/v1/embeddings", tags=["🔢 Embeddings"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["🛠️ Tools"])
app.include_router(chains.router, prefix="/api/v1/chains", tags=["⛓️ Chains"])


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

