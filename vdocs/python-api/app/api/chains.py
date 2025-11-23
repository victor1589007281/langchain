"""Chains API - 链式操作接口"""

from fastapi import APIRouter, HTTPException
import logging

from app.models.schemas import ChainRequest, ChainResponse, ChainType
from app.core.config import settings

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableParallel, RunnableLambda
except ImportError as e:
    logging.warning(f"LangChain imports failed: {e}")

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/execute", response_model=ChainResponse)
async def execute_chain(request: ChainRequest):
    """
    执行链式操作

    根据配置执行不同类型的链。

    - **chain_type**: 链类型（simple/sequential/parallel/conditional）
    - **steps**: 链步骤配置
    - **input**: 输入数据
    """
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API Key 未配置"
            )

        logger.info(f"执行 {request.chain_type} 链，步骤数: {len(request.steps)}")

        if request.chain_type == ChainType.SIMPLE:
            result = await _execute_simple_chain(request)
        elif request.chain_type == ChainType.SEQUENTIAL:
            result = await _execute_sequential_chain(request)
        elif request.chain_type == ChainType.PARALLEL:
            result = await _execute_parallel_chain(request)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的链类型: {request.chain_type}"
            )

        return ChainResponse(
            output=result,
            chain_type=request.chain_type,
            steps_executed=len(request.steps)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"链执行错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_simple_chain(request: ChainRequest):
    """执行简单链"""
    # 创建一个简单的 prompt | model | parser 链

    prompt = ChatPromptTemplate.from_template(
        request.steps[0].config.get("template", "{input}")
    )

    model = ChatOpenAI(
        model=settings.DEFAULT_MODEL,
        temperature=settings.DEFAULT_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY
    )

    parser = StrOutputParser()

    chain = prompt | model | parser

    return chain.invoke({"input": request.input})


async def _execute_sequential_chain(request: ChainRequest):
    """执行顺序链"""
    # 依次执行多个步骤

    result = request.input

    for step in request.steps:
        step_type = step.type

        if step_type == "prompt":
            template = step.config.get("template", "{input}")
            prompt = ChatPromptTemplate.from_template(template)
            result = prompt.invoke({"input": result})

        elif step_type == "model":
            model = ChatOpenAI(
                model=step.config.get("model", settings.DEFAULT_MODEL),
                temperature=step.config.get("temperature", settings.DEFAULT_TEMPERATURE),
                openai_api_key=settings.OPENAI_API_KEY
            )
            result = model.invoke(result)

        elif step_type == "parser":
            parser = StrOutputParser()
            result = parser.invoke(result)

        elif step_type == "transform":
            # 自定义转换
            transform_type = step.config.get("transform_type")
            if transform_type == "upper":
                result = str(result).upper()
            elif transform_type == "lower":
                result = str(result).lower()
            elif transform_type == "length":
                result = len(str(result))

    return result


async def _execute_parallel_chain(request: ChainRequest):
    """执行并行链"""
    # 并行执行多个步骤

    parallel_chains = {}

    for i, step in enumerate(request.steps):
        name = step.config.get("name", f"step_{i}")
        template = step.config.get("template", "{input}")

        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            temperature=settings.DEFAULT_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        parser = StrOutputParser()

        parallel_chains[name] = prompt | model | parser

    # 创建并行运行
    parallel = RunnableParallel(parallel_chains)

    return parallel.invoke({"input": request.input})


@router.get("/examples")
async def get_chain_examples():
    """
    获取链示例

    返回各种类型链的配置示例。
    """
    return {
        "examples": [
            {
                "name": "简单问答链",
                "chain_type": "simple",
                "description": "最基本的提示-模型-解析链",
                "config": {
                    "chain_type": "simple",
                    "steps": [
                        {
                            "type": "prompt",
                            "config": {
                                "template": "请回答：{input}"
                            }
                        }
                    ],
                    "input": "什么是 LangChain？"
                }
            },
            {
                "name": "多步处理链",
                "chain_type": "sequential",
                "description": "依次执行多个步骤",
                "config": {
                    "chain_type": "sequential",
                    "steps": [
                        {"type": "prompt", "config": {"template": "将以下文本翻译成英文：{input}"}},
                        {"type": "model", "config": {}},
                        {"type": "parser", "config": {}}
                    ],
                    "input": "你好，世界"
                }
            },
            {
                "name": "并行处理链",
                "chain_type": "parallel",
                "description": "同时执行多个任务",
                "config": {
                    "chain_type": "parallel",
                    "steps": [
                        {
                            "type": "chain",
                            "config": {
                                "name": "summary",
                                "template": "请总结：{input}"
                            }
                        },
                        {
                            "type": "chain",
                            "config": {
                                "name": "keywords",
                                "template": "提取关键词：{input}"
                            }
                        }
                    ],
                    "input": "LangChain 是一个强大的 LLM 应用框架"
                }
            }
        ]
    }

