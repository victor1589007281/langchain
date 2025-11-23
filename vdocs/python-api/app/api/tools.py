"""Tools API - 工具管理接口"""

from fastapi import APIRouter, HTTPException
import logging

from app.models.schemas import ToolCallRequest, ToolCallResponse
from app.api.agent import AVAILABLE_TOOLS

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/list")
async def list_tools():
    """
    获取所有可用工具

    返回系统中所有预定义工具的列表。
    """
    tools = []

    for name, tool_func in AVAILABLE_TOOLS.items():
        tools.append({
            "name": name,
            "description": tool_func.description,
            "parameters": str(tool_func.args) if hasattr(tool_func, "args") else "无参数"
        })

    return {"tools": tools, "count": len(tools)}


@router.post("/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """
    直接调用工具

    不通过 Agent，直接调用指定的工具。

    - **tool_name**: 工具名称
    - **arguments**: 工具参数
    """
    try:
        if request.tool_name not in AVAILABLE_TOOLS:
            raise HTTPException(
                status_code=404,
                detail=f"工具 '{request.tool_name}' 不存在"
            )

        tool = AVAILABLE_TOOLS[request.tool_name]

        # 调用工具
        logger.info(f"调用工具: {request.tool_name}, 参数: {request.arguments}")

        # 根据工具的参数要求调用
        if request.arguments:
            # 获取第一个参数值（大多数工具只有一个参数）
            if len(request.arguments) == 1:
                arg_value = list(request.arguments.values())[0]
                result = tool.invoke(arg_value)
            else:
                result = tool.invoke(request.arguments)
        else:
            result = tool.invoke({})

        return ToolCallResponse(
            result=result,
            tool_name=request.tool_name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"工具调用错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tool_name}")
async def get_tool_info(tool_name: str):
    """
    获取特定工具的详细信息

    返回指定工具的完整信息。
    """
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(
            status_code=404,
            detail=f"工具 '{tool_name}' 不存在"
        )

    tool = AVAILABLE_TOOLS[tool_name]

    return {
        "name": tool_name,
        "description": tool.description,
        "parameters": str(tool.args) if hasattr(tool, "args") else "无参数",
        "func": tool.func.__name__ if hasattr(tool, "func") else None
    }

