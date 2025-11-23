"""RAG API - 检索增强生成接口"""

from fastapi import APIRouter, HTTPException
import logging
from pathlib import Path

from app.models.schemas import RAGIndexRequest, RAGQueryRequest, RAGResponse, Document
from app.core.config import settings

try:
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.documents import Document as LangChainDocument
except ImportError as e:
    logging.warning(f"LangChain imports failed: {e}")

logger = logging.getLogger(__name__)
router = APIRouter()

# 存储向量库实例
_vector_stores = {}


@router.post("/index")
async def create_index(request: RAGIndexRequest):
    """
    创建 RAG 索引

    将文档切分并向量化，存储到向量数据库中。

    - **documents**: 文档列表
    - **collection_name**: 集合名称（默认: default）
    - **chunk_size**: 文本块大小
    - **chunk_overlap**: 文本块重叠
    """
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API Key 未配置"
            )

        # 创建文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
        )

        # 转换文档格式
        documents = [
            LangChainDocument(
                page_content=doc.content,
                metadata=doc.metadata
            )
            for doc in request.documents
        ]

        # 分割文档
        splits = text_splitter.split_documents(documents)
        logger.info(f"文档分割完成: {len(documents)} -> {len(splits)} 块")

        # 创建嵌入模型
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

        # 创建或更新向量存储
        persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY) / request.collection_name
        persist_dir.mkdir(parents=True, exist_ok=True)

        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            collection_name=request.collection_name,
            persist_directory=str(persist_dir)
        )

        # 缓存向量存储
        _vector_stores[request.collection_name] = vectorstore

        logger.info(f"索引创建完成: {request.collection_name}")

        return {
            "status": "success",
            "collection_name": request.collection_name,
            "documents_count": len(documents),
            "chunks_count": len(splits)
        }

    except Exception as e:
        logger.error(f"创建索引错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=RAGResponse)
async def query_rag(request: RAGQueryRequest):
    """
    RAG 查询

    基于向量检索增强的问答。

    - **query**: 查询问题
    - **collection_name**: 集合名称
    - **k**: 返回的相关文档数量
    - **config**: 模型配置
    """
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API Key 未配置"
            )

        # 获取或加载向量存储
        if request.collection_name not in _vector_stores:
            persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY) / request.collection_name

            if not persist_dir.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"集合 '{request.collection_name}' 不存在"
                )

            embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            vectorstore = Chroma(
                collection_name=request.collection_name,
                embedding_function=embeddings,
                persist_directory=str(persist_dir)
            )
            _vector_stores[request.collection_name] = vectorstore
        else:
            vectorstore = _vector_stores[request.collection_name]

        # 检索相关文档
        docs = vectorstore.similarity_search(request.query, k=request.k)
        logger.info(f"检索到 {len(docs)} 个相关文档")

        # 构建提示
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = ChatPromptTemplate.from_template("""
请基于以下上下文回答问题。如果上下文中没有相关信息，请说"我不知道"。

上下文:
{context}

问题: {question}

回答:""")

        # 获取模型配置
        config = request.config or {}
        model_name = config.model if config else settings.DEFAULT_MODEL
        temperature = config.temperature if config else settings.DEFAULT_TEMPERATURE

        # 创建 LLM
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 生成答案
        chain = prompt | llm
        response = chain.invoke({
            "context": context,
            "question": request.query
        })

        # 转换源文档格式
        sources = [
            Document(
                content=doc.page_content,
                metadata=doc.metadata
            )
            for doc in docs
        ]

        return RAGResponse(
            answer=response.content,
            sources=sources,
            model=model_name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG 查询错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
async def list_collections():
    """
    列出所有可用的集合

    返回已创建的向量存储集合列表。
    """
    try:
        persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)

        if not persist_dir.exists():
            return {"collections": []}

        collections = [
            d.name for d in persist_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        return {"collections": collections}

    except Exception as e:
        logger.error(f"列出集合错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """
    删除集合

    删除指定的向量存储集合。
    """
    try:
        persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY) / collection_name

        if not persist_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"集合 '{collection_name}' 不存在"
            )

        # 从缓存中移除
        if collection_name in _vector_stores:
            del _vector_stores[collection_name]

        # 删除目录
        import shutil
        shutil.rmtree(persist_dir)

        logger.info(f"集合已删除: {collection_name}")

        return {
            "status": "success",
            "message": f"集合 '{collection_name}' 已删除"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除集合错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

