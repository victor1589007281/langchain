"""Agent API - 智能代理接口"""

from fastapi import APIRouter, HTTPException
import logging

from app.models.schemas import AgentRequest, AgentResponse, AgentStep
from app.core.config import settings

try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.tools import tool
except ImportError as e:
    logging.warning(f"LangChain imports failed: {e}")

logger = logging.getLogger(__name__)
router = APIRouter()


# 预定义的工具集合
@tool
def calculator(expression: str) -> str:
    """
    计算数学表达式

    Args:
        expression: 数学表达式，例如 "2 + 2" 或 "10 * 5"
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def web_search(query: str) -> str:
    """
    模拟网络搜索（演示用）

    Args:
        query: 搜索查询
    """
    # 这里只是模拟，实际应该调用搜索 API
    return f"搜索结果: 关于 '{query}' 的信息（这是模拟结果）"


@tool
def get_current_time() -> str:
    """
    获取当前时间

    无需参数
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 所有可用工具
AVAILABLE_TOOLS = {
    "calculator": calculator,
    "web_search": web_search,
    "get_current_time": get_current_time
}


@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """
    执行 Agent 任务

    创建并执行一个能够使用工具的智能代理。

    - **task**: 任务描述
    - **tools**: 可用工具列表（从预定义工具中选择）
    - **max_iterations**: 最大迭代次数
    - **config**: 模型配置
    """
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API Key 未配置"
            )

        # 选择工具
        if not request.tools:
            tools = list(AVAILABLE_TOOLS.values())
        else:
            tools = []
            for tool_name in request.tools:
                if tool_name not in AVAILABLE_TOOLS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"未知工具: {tool_name}"
                    )
                tools.append(AVAILABLE_TOOLS[tool_name])

        logger.info(f"使用工具: {[t.name for t in tools]}")

        # 获取模型配置
        config = request.config or {}
        model_name = config.model if config else settings.DEFAULT_MODEL
        temperature = config.temperature if config else 0.0  # Agent 使用较低温度

        # 创建 LLM
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能助手，可以使用工具来完成任务。

请按以下格式思考:
1. 分析任务需求
2. 决定使用哪个工具
3. 执行工具并观察结果
4. 如果需要，继续使用其他工具
5. 给出最终答案

当你有了最终答案时，请明确说明。"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # 创建 Agent
        agent = create_tool_calling_agent(llm, tools, prompt)

        # 创建 Agent 执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            max_iterations=request.max_iterations,
            verbose=True,
            return_intermediate_steps=True
        )

        # 执行 Agent
        logger.info(f"执行 Agent 任务: {request.task}")
        result = agent_executor.invoke({"input": request.task})

        # 提取步骤信息
        steps = []
        if "intermediate_steps" in result:
            for action, observation in result["intermediate_steps"]:
                steps.append(AgentStep(
                    thought=action.log if hasattr(action, "log") else "执行工具",
                    action=f"{action.tool}: {action.tool_input}",
                    observation=str(observation)
                ))

        return AgentResponse(
            result=result["output"],
            steps=steps,
            iterations=len(steps)
        )

    except Exception as e:
        logger.error(f"Agent 执行错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def list_tools():
    """
    获取可用工具列表

    返回所有预定义工具的信息。
    """
    tools_info = []

    for name, tool_func in AVAILABLE_TOOLS.items():
        tools_info.append({
            "name": name,
            "description": tool_func.description,
            "parameters": tool_func.args if hasattr(tool_func, "args") else {}
        })

    return {"tools": tools_info}

