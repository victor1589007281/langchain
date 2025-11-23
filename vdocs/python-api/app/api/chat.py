"""Chat API - 对话接口"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
from typing import AsyncGenerator

from app.models.schemas import ChatRequest, ChatResponse
from app.core.config import settings

# 延迟导入，避免在没有 API key 时失败
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
except ImportError as e:
    logging.warning(f"LangChain imports failed: {e}")

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/invoke", response_model=ChatResponse)
async def chat_invoke(request: ChatRequest):
    """
    同步对话接口

    发送消息并获取 AI 回复。

    - **messages**: 消息列表（包含角色和内容）
    - **config**: 可选的模型配置
    - **system_message**: 可选的系统提示
    """
    try:
        # 检查 API Key
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API Key 未配置。请设置 OPENAI_API_KEY 环境变量"
            )

        # 获取模型配置
        config = request.config or {}
        model_name = config.model if config else settings.DEFAULT_MODEL
        temperature = config.temperature if config else settings.DEFAULT_TEMPERATURE

        # 创建 ChatModel
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 构建消息列表
        messages = []

        # 添加系统消息
        if request.system_message:
            messages.append(SystemMessage(content=request.system_message))

        # 添加用户消息
        for msg in request.messages:
            if msg.role == "system":
                messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        # 调用模型
        logger.info(f"调用模型 {model_name}，消息数: {len(messages)}")
        response = llm.invoke(messages)

        return ChatResponse(
            message=response.content,
            model=model_name,
            usage=response.response_metadata.get("token_usage") if hasattr(response, "response_metadata") else None
        )

    except Exception as e:
        logger.error(f"Chat invoke 错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    流式对话接口

    发送消息并流式接收 AI 回复。

    返回 Server-Sent Events (SSE) 流。
    """

    async def generate() -> AsyncGenerator[str, None]:
        try:
            # 检查 API Key
            if not settings.OPENAI_API_KEY:
                yield f"data: {{\"error\": \"OpenAI API Key 未配置\"}}\n\n"
                return

            # 获取模型配置
            config = request.config or {}
            model_name = config.model if config else settings.DEFAULT_MODEL
            temperature = config.temperature if config else settings.DEFAULT_TEMPERATURE

            # 创建 ChatModel
            llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=True
            )

            # 构建消息列表
            messages = []
            if request.system_message:
                messages.append(SystemMessage(content=request.system_message))

            for msg in request.messages:
                if msg.role == "system":
                    messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))

            # 流式调用
            logger.info(f"流式调用模型 {model_name}")
            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield f"data: {{\"content\": \"{chunk.content}\"}}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Chat stream 错误: {e}", exc_info=True)
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.get("/models")
async def list_models():
    """
    获取可用模型列表

    返回支持的模型列表及其配置。
    """
    return {
        "models": [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "description": "最强大的模型，适合复杂任务"
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "description": "快速且经济的模型，适合一般任务"
            },
            {
                "id": "gpt-4-turbo-preview",
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "description": "GPT-4 的优化版本，更快更便宜"
            }
        ],
        "default_model": settings.DEFAULT_MODEL
    }

