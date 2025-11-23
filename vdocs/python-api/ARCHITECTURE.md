# LangChain API Service 架构文档

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  (浏览器、移动应用、其他服务)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Layer                           │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Chat    │   RAG    │  Agent   │Embeddings│ Chains  │  │
│  │  API     │   API    │   API    │   API    │  API    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangChain Core                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Runnables │ Chains │ Agents │ Tools │ Prompts      │  │
│  └──────────────────────────────────────────────────────┘  │
└────┬───────────────────────┬──────────────────┬────────────┘
     │                       │                   │
     ▼                       ▼                   ▼
┌─────────┐         ┌────────────────┐   ┌──────────────┐
│  LLM    │         │  Vector Store  │   │   Tools      │
│ OpenAI  │         │    Chroma      │   │  Calculator  │
│Anthropic│         │                │   │  WebSearch   │
└─────────┘         └────────────────┘   └──────────────┘
```

## 目录结构说明

### app/ - 应用代码

```
app/
├── main.py                 # FastAPI 应用入口
│   ├── lifespan 管理
│   ├── 中间件配置
│   ├── 路由注册
│   └── 异常处理
│
├── core/                   # 核心模块
│   ├── config.py          # 配置管理（Pydantic Settings）
│   └── logging_config.py  # 日志配置
│
├── models/                 # 数据模型
│   └── schemas.py         # Pydantic 模型定义
│
└── api/                    # API 端点
    ├── chat.py            # 对话接口
    ├── rag.py             # RAG 接口
    ├── agent.py           # Agent 接口
    ├── embeddings.py      # 嵌入接口
    ├── tools.py           # 工具接口
    └── chains.py          # 链式接口
```

## 关键组件

### 1. FastAPI 应用 (main.py)

**职责**：
- 应用初始化和配置
- 路由注册
- 中间件管理（CORS、日志）
- 全局异常处理
- 生命周期管理

**关键代码**：
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    yield
    # 关闭时清理

app = FastAPI(lifespan=lifespan)
```

### 2. 配置管理 (core/config.py)

**职责**：
- 环境变量读取
- 配置验证
- 默认值管理

**特点**：
- 使用 Pydantic Settings
- 支持 .env 文件
- 类型安全

### 3. API 端点层

#### Chat API (api/chat.py)

**功能**：
- 同步对话（invoke）
- 流式对话（stream）
- 模型列表

**实现**：
```python
# 同步对话
ChatOpenAI -> invoke -> AIMessage

# 流式对话
ChatOpenAI -> astream -> AsyncIterator[AIMessageChunk]
```

#### RAG API (api/rag.py)

**功能**：
- 文档索引（index）
- 向量搜索（query）
- 集合管理

**实现**：
```python
Documents -> TextSplitter -> Embeddings -> Chroma
Query -> Embeddings -> Similarity Search -> LLM -> Answer
```

#### Agent API (api/agent.py)

**功能**：
- Agent 执行
- 工具管理
- 多步推理

**实现**：
```python
Task -> create_tool_calling_agent -> AgentExecutor -> Result
```

#### Embeddings API (api/embeddings.py)

**功能**：
- 文本向量化
- 相似度计算
- 模型选择

**实现**：
```python
Texts -> OpenAIEmbeddings -> Vectors
Vector1 + Vector2 -> Cosine Similarity -> Score
```

#### Tools API (api/tools.py)

**功能**：
- 工具列表
- 工具调用
- 工具信息查询

**预定义工具**：
- calculator: 数学计算
- web_search: 网络搜索（模拟）
- get_current_time: 获取时间

#### Chains API (api/chains.py)

**功能**：
- 简单链（Simple）
- 顺序链（Sequential）
- 并行链（Parallel）

**实现**：
```python
# Simple: Prompt | Model | Parser
# Sequential: Step1 -> Step2 -> Step3
# Parallel: RunnableParallel({...})
```

## 数据流

### Chat 流程

```
Request (messages)
  -> ChatRequest 验证
  -> 构建 Message 列表
  -> ChatOpenAI.invoke()
  -> AIMessage
  -> ChatResponse
```

### RAG 流程

```
索引阶段:
Documents
  -> RecursiveCharacterTextSplitter
  -> Document Chunks
  -> OpenAIEmbeddings
  -> Chroma.from_documents()

查询阶段:
Query
  -> OpenAIEmbeddings.embed_query()
  -> Chroma.similarity_search()
  -> Retrieved Documents
  -> Prompt | LLM
  -> Answer + Sources
```

### Agent 流程

```
Task + Tools
  -> create_tool_calling_agent()
  -> AgentExecutor
  -> Loop:
      - LLM 决策
      - Tool 调用
      - 观察结果
      - 继续或结束
  -> Final Answer
```

## 错误处理

### 层次化错误处理

1. **API 层**：捕获并转换为 HTTPException
2. **LangChain 层**：捕获 LangChain 特定错误
3. **全局层**：全局异常处理器

```python
try:
    # API 逻辑
except HTTPException:
    raise  # 直接抛出
except Exception as e:
    logger.error(f"错误: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

## 性能优化

### 1. 缓存策略

- **向量存储缓存**：避免重复加载
- **LLM 缓存**：相同请求复用结果

### 2. 异步处理

- 所有 API 端点都是异步的
- 使用 AsyncIterator 实现流式输出
- 支持并发请求

### 3. 批处理

- Embeddings 支持批量处理
- Agent 支持批量任务

## 安全性

### 1. API Key 管理

- 环境变量存储
- 不在代码中硬编码
- 支持多个 Provider

### 2. 输入验证

- Pydantic 模型验证
- 类型检查
- 长度限制

### 3. 错误信息

- 不泄露敏感信息
- 记录详细日志
- 返回友好错误

## 监控和日志

### 日志级别

- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息

### 日志输出

- 控制台：实时查看
- 文件：持久化存储
- 结构化：JSON 格式

### 健康检查

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "LangChain API",
        "version": "1.0.0"
    }
```

## 扩展性

### 添加新的 API

1. 在 `app/api/` 创建新文件
2. 定义路由和处理函数
3. 在 `main.py` 注册路由
4. 在 `schemas.py` 定义数据模型

### 添加新的工具

```python
@tool
def new_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result

# 注册到 AVAILABLE_TOOLS
```

### 添加新的模型 Provider

```python
from langchain_anthropic import ChatAnthropic

if settings.ANTHROPIC_API_KEY:
    anthropic_model = ChatAnthropic(...)
```

## 部署架构

### Docker 单容器

```
Docker Container
├── FastAPI App (Port 8000)
├── Data Volume (/app/data)
└── Logs Volume (/app/logs)
```

### Docker Compose

```
Services:
└── langchain-api
    ├── Volumes
    │   ├── ./data:/app/data
    │   └── ./logs:/app/logs
    └── Environment
        └── .env file
```

### Kubernetes

```
Deployment (3 replicas)
├── ConfigMap (环境变量)
├── Secret (API Keys)
├── PersistentVolume (数据)
└── Service (LoadBalancer)
```

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 0.109.0 |
| ASGI 服务器 | Uvicorn | 0.27.0 |
| LLM 框架 | LangChain | 0.1.0 |
| 向量存储 | ChromaDB | 0.4.22 |
| 数据验证 | Pydantic | 2.5.3 |
| 容器化 | Docker | - |

## 最佳实践

### 1. 配置管理

- 使用环境变量
- 不提交 .env 文件
- 提供 .env.example

### 2. 错误处理

- 捕获所有异常
- 记录详细日志
- 返回友好错误

### 3. 性能优化

- 使用异步 IO
- 实现缓存策略
- 批处理请求

### 4. 安全性

- 验证所有输入
- 保护 API Keys
- 实施速率限制

### 5. 可维护性

- 模块化设计
- 代码注释
- 类型提示

## 未来改进

- [ ] 添加认证和授权
- [ ] 实现速率限制
- [ ] 添加更多 LLM Provider
- [ ] 支持更多向量存储
- [ ] 添加监控和追踪
- [ ] 实现缓存层
- [ ] 添加单元测试
- [ ] 性能基准测试
- [ ] API 版本管理
- [ ] WebSocket 支持

---

**文档版本**: 1.0
**最后更新**: 2025-11-23

