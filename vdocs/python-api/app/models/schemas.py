"""API 数据模型和 Schemas"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum


# ==================== 通用模型 ====================

class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """消息模型"""
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")


class ModelConfig(BaseModel):
    """模型配置"""
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, description="最大token数")
    top_p: float = Field(default=1.0, ge=0, le=1, description="Top P 采样参数")
    stream: bool = Field(default=False, description="是否流式输出")


# ==================== Chat API ====================

class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[Message] = Field(..., description="消息列表")
    config: Optional[ModelConfig] = Field(default=None, description="模型配置")
    system_message: Optional[str] = Field(default=None, description="系统提示")


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str = Field(..., description="AI 回复内容")
    model: str = Field(..., description="使用的模型")
    usage: Optional[Dict[str, int]] = Field(default=None, description="Token 使用情况")


# ==================== RAG API ====================

class Document(BaseModel):
    """文档模型"""
    content: str = Field(..., description="文档内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文档元数据")


class RAGIndexRequest(BaseModel):
    """RAG 索引请求"""
    documents: List[Document] = Field(..., description="文档列表")
    collection_name: str = Field(default="default", description="集合名称")
    chunk_size: int = Field(default=1000, description="文本块大小")
    chunk_overlap: int = Field(default=200, description="文本块重叠")


class RAGQueryRequest(BaseModel):
    """RAG 查询请求"""
    query: str = Field(..., description="查询问题")
    collection_name: str = Field(default="default", description="集合名称")
    k: int = Field(default=4, description="返回的文档数量")
    config: Optional[ModelConfig] = Field(default=None, description="模型配置")


class RAGResponse(BaseModel):
    """RAG 响应"""
    answer: str = Field(..., description="生成的答案")
    sources: List[Document] = Field(..., description="来源文档")
    model: str = Field(..., description="使用的模型")


# ==================== Agent API ====================

class ToolDefinition(BaseModel):
    """工具定义"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")


class AgentRequest(BaseModel):
    """Agent 请求"""
    task: str = Field(..., description="任务描述")
    tools: List[str] = Field(default_factory=list, description="可用工具列表")
    max_iterations: int = Field(default=5, description="最大迭代次数")
    config: Optional[ModelConfig] = Field(default=None, description="模型配置")


class AgentStep(BaseModel):
    """Agent 执行步骤"""
    thought: str = Field(..., description="思考过程")
    action: Optional[str] = Field(default=None, description="执行的动作")
    observation: Optional[str] = Field(default=None, description="观察结果")


class AgentResponse(BaseModel):
    """Agent 响应"""
    result: str = Field(..., description="最终结果")
    steps: List[AgentStep] = Field(..., description="执行步骤")
    iterations: int = Field(..., description="迭代次数")


# ==================== Embeddings API ====================

class EmbeddingsRequest(BaseModel):
    """嵌入请求"""
    texts: List[str] = Field(..., description="文本列表")
    model: str = Field(default="text-embedding-ada-002", description="嵌入模型")


class EmbeddingsResponse(BaseModel):
    """嵌入响应"""
    embeddings: List[List[float]] = Field(..., description="嵌入向量列表")
    model: str = Field(..., description="使用的模型")
    usage: Optional[Dict[str, int]] = Field(default=None, description="使用情况")


# ==================== Tools API ====================

class ToolCallRequest(BaseModel):
    """工具调用请求"""
    tool_name: str = Field(..., description="工具名称")
    arguments: Dict[str, Any] = Field(..., description="工具参数")


class ToolCallResponse(BaseModel):
    """工具调用响应"""
    result: Any = Field(..., description="工具执行结果")
    tool_name: str = Field(..., description="工具名称")


# ==================== Chains API ====================

class ChainType(str, Enum):
    """链类型枚举"""
    SIMPLE = "simple"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class ChainStep(BaseModel):
    """链步骤"""
    type: str = Field(..., description="步骤类型")
    config: Dict[str, Any] = Field(default_factory=dict, description="步骤配置")


class ChainRequest(BaseModel):
    """链请求"""
    chain_type: ChainType = Field(..., description="链类型")
    steps: List[ChainStep] = Field(..., description="链步骤")
    input: Union[str, Dict[str, Any]] = Field(..., description="输入数据")


class ChainResponse(BaseModel):
    """链响应"""
    output: Any = Field(..., description="输出结果")
    chain_type: str = Field(..., description="链类型")
    steps_executed: int = Field(..., description="执行的步骤数")

