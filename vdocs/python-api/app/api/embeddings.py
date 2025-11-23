"""Embeddings API - 文本向量化接口"""

from fastapi import APIRouter, HTTPException
import logging

from app.models.schemas import EmbeddingsRequest, EmbeddingsResponse
from app.core.config import settings

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError as e:
    logging.warning(f"LangChain imports failed: {e}")

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/embed", response_model=EmbeddingsResponse)
async def create_embeddings(request: EmbeddingsRequest):
    """
    创建文本嵌入向量

    将文本转换为向量表示，可用于相似度计算、聚类等。

    - **texts**: 文本列表
    - **model**: 嵌入模型名称
    """
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API Key 未配置"
            )

        # 创建嵌入模型
        embeddings_model = OpenAIEmbeddings(
            model=request.model,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 生成嵌入
        logger.info(f"生成 {len(request.texts)} 个文本的嵌入")
        vectors = embeddings_model.embed_documents(request.texts)

        # 获取使用统计（如果可用）
        usage = None

        return EmbeddingsResponse(
            embeddings=vectors,
            model=request.model,
            usage=usage
        )

    except Exception as e:
        logger.error(f"生成嵌入错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/similarity")
async def compute_similarity(text1: str, text2: str, model: str = "text-embedding-ada-002"):
    """
    计算两个文本的相似度

    使用余弦相似度计算两个文本的相似程度。

    - **text1**: 第一个文本
    - **text2**: 第二个文本
    - **model**: 嵌入模型名称
    """
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API Key 未配置"
            )

        # 创建嵌入模型
        embeddings_model = OpenAIEmbeddings(
            model=model,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 生成嵌入
        vectors = embeddings_model.embed_documents([text1, text2])
        vec1, vec2 = vectors[0], vectors[1]

        # 计算余弦相似度
        import numpy as np

        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        similarity = dot_product / (norm1 * norm2)

        return {
            "similarity": float(similarity),
            "text1": text1,
            "text2": text2,
            "model": model
        }

    except Exception as e:
        logger.error(f"计算相似度错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_embedding_models():
    """
    获取可用的嵌入模型列表

    返回支持的嵌入模型信息。
    """
    return {
        "models": [
            {
                "id": "text-embedding-ada-002",
                "name": "Ada-002",
                "provider": "OpenAI",
                "dimensions": 1536,
                "description": "OpenAI 的标准嵌入模型"
            },
            {
                "id": "text-embedding-3-small",
                "name": "Embedding-3-Small",
                "provider": "OpenAI",
                "dimensions": 1536,
                "description": "更新的嵌入模型，性能更好"
            },
            {
                "id": "text-embedding-3-large",
                "name": "Embedding-3-Large",
                "provider": "OpenAI",
                "dimensions": 3072,
                "description": "最大的嵌入模型，精度最高"
            }
        ]
    }

