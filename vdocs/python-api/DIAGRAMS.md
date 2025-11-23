# LangChain API Service - 架构图表

本文档包含项目的各种架构图和流程图，使用 Mermaid 语法绘制。

## 📊 系统架构图

### 整体架构

```mermaid
graph TB
    subgraph clientLayer["**客户端层**"]
        Browser["**浏览器**"]
        Mobile["**移动应用**"]
        Service["**其他服务**"]
    end

    subgraph apiLayer["**API 层 (FastAPI)**"]
        ChatAPI["**💬 Chat API**<br/>对话接口"]
        RAGAPI["**📚 RAG API**<br/>检索增强"]
        AgentAPI["**🤖 Agent API**<br/>智能代理"]
        EmbedAPI["**🔢 Embed API**<br/>向量化"]
        ToolsAPI["**🛠️ Tools API**<br/>工具管理"]
        ChainsAPI["**⛓️ Chains API**<br/>链式操作"]
    end

    subgraph coreLayer["**LangChain 核心层**"]
        Runnables["**Runnables**<br/>可执行抽象"]
        Chains["**Chains**<br/>链式组合"]
        Agents["**Agents**<br/>智能代理"]
        Tools["**Tools**<br/>工具系统"]
    end

    subgraph dataLayer["**数据层**"]
        Chroma["**ChromaDB**<br/>向量存储"]
        Files["**文件系统**<br/>数据持久化"]
    end

    subgraph externalLayer["**外部服务**"]
        OpenAI["**OpenAI API**<br/>LLM 服务"]
        Anthropic["**Anthropic API**<br/>LLM 服务"]
    end

    Browser --> ChatAPI
    Mobile --> RAGAPI
    Service --> AgentAPI

    ChatAPI --> Runnables
    RAGAPI --> Chains
    AgentAPI --> Agents
    EmbedAPI --> Tools
    ToolsAPI --> Tools
    ChainsAPI --> Runnables

    Runnables --> OpenAI
    Chains --> Chroma
    Agents --> Tools

    Chroma --> Files

    style clientLayer fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style apiLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:3px
    style coreLayer fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style dataLayer fill:#fff3e0,stroke:#e65100,stroke-width:3px
    style externalLayer fill:#fce4ec,stroke:#880e4f,stroke-width:3px
```

## 🔄 数据流程图

### Chat API 流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as Chat API
    participant LangChain as LangChain
    participant OpenAI as OpenAI API

    Client->>API: POST /api/v1/chat/invoke
    Note over Client,API: {"messages": [...]}

    API->>API: 验证请求数据
    API->>LangChain: 构建消息列表
    LangChain->>OpenAI: 调用 LLM
    OpenAI-->>LangChain: 返回 AI 响应
    LangChain-->>API: AIMessage
    API-->>Client: ChatResponse

    Note over Client,API: {"message": "...", "model": "..."}
```

### RAG 查询流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as RAG API
    participant Chroma as ChromaDB
    participant LLM as LLM

    Note over Client,API: 第一步: 创建索引
    Client->>API: POST /api/v1/rag/index
    API->>API: 文档分割
    API->>Chroma: 存储向量
    Chroma-->>API: 索引完成
    API-->>Client: 成功响应

    Note over Client,API: 第二步: 查询
    Client->>API: POST /api/v1/rag/query
    API->>Chroma: 相似度搜索
    Chroma-->>API: 相关文档
    API->>LLM: 生成答案
    LLM-->>API: AI 响应
    API-->>Client: 答案 + 来源
```

### Agent 执行流程

```mermaid
stateDiagram-v2
    [*] --> 接收任务
    接收任务 --> 思考
    思考 --> 选择工具
    选择工具 --> 执行工具
    执行工具 --> 观察结果
    观察结果 --> 判断完成

    判断完成 --> 思考: 未完成
    判断完成 --> 返回结果: 已完成
    返回结果 --> [*]

    note right of 思考
        LLM 分析任务
        决定下一步行动
    end note

    note right of 执行工具
        calculator
        web_search
        get_current_time
    end note
```

## 🗂️ 项目结构图

```mermaid
graph LR
    subgraph projectRoot["**python-api/**"]
        subgraph appDir["**app/**"]
            Main["**main.py**<br/>FastAPI 入口"]

            subgraph coreDir["**core/**"]
                Config["**config.py**<br/>配置管理"]
                Logging["**logging_config.py**<br/>日志配置"]
            end

            subgraph modelsDir["**models/**"]
                Schemas["**schemas.py**<br/>数据模型"]
            end

            subgraph apiDir["**api/**"]
                Chat["**chat.py**"]
                RAG["**rag.py**"]
                Agent["**agent.py**"]
                Embed["**embeddings.py**"]
                Tools["**tools.py**"]
                Chains["**chains.py**"]
            end
        end

        subgraph scriptsDir["**scripts/**"]
            Build["**build.sh**"]
            Deploy["**deploy.sh**"]
            Stop["**stop.sh**"]
            Logs["**logs.sh**"]
        end

        subgraph configFiles["**配置文件**"]
            Dockerfile["**Dockerfile**"]
            Compose["**docker-compose.yml**"]
            Req["**requirements.txt**"]
            Env["**.env.example**"]
        end

        subgraph docsFiles["**文档**"]
            README["**README.md**"]
            ARCH["**ARCHITECTURE.md**"]
            QUICK["**QUICKSTART.md**"]
        end
    end

    Main --> coreDir
    Main --> apiDir
    apiDir --> modelsDir

    style projectRoot fill:#f0f4f8,stroke:#2c3e50,stroke-width:2px
    style appDir fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style coreDir fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    style modelsDir fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style apiDir fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style scriptsDir fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style configFiles fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style docsFiles fill:#e0f2f1,stroke:#00796b,stroke-width:2px
```

## 🔌 API 端点地图

```mermaid
mindmap
  root((LangChain API))
    Chat API
      invoke
        同步对话
      stream
        流式对话
      models
        模型列表
    RAG API
      index
        创建索引
      query
        RAG 查询
      collections
        集合管理
      delete
        删除集合
    Agent API
      execute
        执行代理
      tools
        工具列表
    Embeddings API
      embed
        文本向量化
      similarity
        相似度计算
      models
        模型列表
    Tools API
      list
        列出工具
      call
        调用工具
      info
        工具信息
    Chains API
      execute
        执行链
      examples
        链示例
```

## 🐳 Docker 部署架构

```mermaid
graph TB
    subgraph dockerHost["**Docker Host**"]
        subgraph container["**langchain-api 容器**"]
            FastAPI["**FastAPI App**<br/>Port 8000"]

            subgraph volumes["**挂载卷**"]
                DataVol["**/app/data**<br/>向量数据"]
                LogsVol["**/app/logs**<br/>日志文件"]
            end
        end

        subgraph hostVolumes["**主机目录**"]
            HostData["**./data**"]
            HostLogs["**./logs**"]
        end
    end

    Internet["**互联网**"] --> FastAPI

    DataVol -.映射.-> HostData
    LogsVol -.映射.-> HostLogs

    FastAPI --> OpenAIAPI["**OpenAI API**"]

    style dockerHost fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style container fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style volumes fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style hostVolumes fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

## 📦 依赖关系图

```mermaid
graph LR
    subgraph appLayer["**应用层**"]
        Main[main.py]
        APIs[API 端点]
    end

    subgraph frameworkLayer["**框架层**"]
        FastAPI[FastAPI]
        Uvicorn[Uvicorn]
        Pydantic[Pydantic]
    end

    subgraph langchainLayer["**LangChain 层**"]
        LC[langchain]
        LCCore[langchain-core]
        LCOpenAI[langchain-openai]
        LCCommunity[langchain-community]
    end

    subgraph dataLayer["**数据层**"]
        ChromaDB[ChromaDB]
        NumPy[NumPy]
    end

    subgraph externalLayer["**外部服务**"]
        OpenAI[OpenAI API]
    end

    Main --> FastAPI
    APIs --> Pydantic
    FastAPI --> Uvicorn

    APIs --> LC
    LC --> LCCore
    LC --> LCOpenAI
    LC --> LCCommunity

    LCCommunity --> ChromaDB
    LCOpenAI --> OpenAI
    ChromaDB --> NumPy

    style appLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style frameworkLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style langchainLayer fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style dataLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style externalLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
```

## 🔐 安全架构

```mermaid
graph TB
    subgraph external["**外部请求**"]
        Request["HTTP 请求"]
    end

    subgraph securityLayer["**安全层**"]
        CORS["**CORS 中间件**<br/>跨域控制"]
        Validation["**输入验证**<br/>Pydantic"]
        EnvVars["**环境变量**<br/>敏感信息"]
    end

    subgraph appLayer["**应用层**"]
        API["**API 端点**"]
    end

    subgraph loggingLayer["**日志层**"]
        Logger["**日志记录**<br/>错误追踪"]
    end

    Request --> CORS
    CORS --> Validation
    Validation --> API
    API --> Logger
    API -.读取.-> EnvVars

    style external fill:#ffebee,stroke:#c62828,stroke-width:2px
    style securityLayer fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style appLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style loggingLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

## 🚀 部署流程图

```mermaid
graph LR
    Start([开始]) --> CheckEnv{检查环境}
    CheckEnv -->|Docker 未安装| InstallDocker[安装 Docker]
    CheckEnv -->|Docker 已安装| BuildImage

    InstallDocker --> BuildImage[构建镜像<br/>build.sh]
    BuildImage --> ConfigEnv[配置环境变量<br/>.env]
    ConfigEnv --> Deploy[部署服务<br/>deploy.sh]
    Deploy --> HealthCheck{健康检查}

    HealthCheck -->|失败| ViewLogs[查看日志<br/>logs.sh]
    ViewLogs --> FixIssue[修复问题]
    FixIssue --> Deploy

    HealthCheck -->|成功| Running[服务运行]
    Running --> End([完成])

    style Start fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style End fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style BuildImage fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px
    style Deploy fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style Running fill:#b2dfdb,stroke:#00695c,stroke-width:2px
```

## 📊 性能架构

```mermaid
graph TB
    subgraph clientReq["**客户端请求**"]
        Req1[请求 1]
        Req2[请求 2]
        Req3[请求 N]
    end

    subgraph asyncLayer["**异步处理层**"]
        Uvicorn["**Uvicorn**<br/>ASGI 服务器"]
        AsyncIO["**AsyncIO**<br/>异步 I/O"]
    end

    subgraph cachingLayer["**缓存层**"]
        VectorCache["**向量存储缓存**"]
        LLMCache["**LLM 缓存**"]
    end

    subgraph processingLayer["**处理层**"]
        Worker1[Worker 1]
        Worker2[Worker 2]
        WorkerN[Worker N]
    end

    Req1 --> Uvicorn
    Req2 --> Uvicorn
    Req3 --> Uvicorn

    Uvicorn --> AsyncIO
    AsyncIO --> VectorCache
    AsyncIO --> LLMCache

    VectorCache --> Worker1
    LLMCache --> Worker2
    AsyncIO --> WorkerN

    style clientReq fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style asyncLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style cachingLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style processingLayer fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```

## 🔄 错误处理流程

```mermaid
flowchart TD
    Start([接收请求]) --> TryBlock{尝试执行}

    TryBlock -->|成功| Success[返回成功响应]
    TryBlock -->|HTTP 异常| HTTPEx[捕获 HTTPException]
    TryBlock -->|其他异常| GenEx[捕获 Exception]

    HTTPEx --> LogHTTP[记录 HTTP 错误]
    GenEx --> LogGen[记录详细错误]

    LogHTTP --> ReturnHTTP[返回 HTTP 错误]
    LogGen --> ReturnGen[返回 500 错误]

    Success --> End([完成])
    ReturnHTTP --> End
    ReturnGen --> End

    style Start fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style TryBlock fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style HTTPEx fill:#ffccbc,stroke:#d84315,stroke-width:2px
    style GenEx fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    style Success fill:#b2dfdb,stroke:#00695c,stroke-width:2px
    style End fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

---

## 📋 图表说明

本文档包含 11 个架构图表：

1. **整体架构** - 展示系统分层结构
2. **Chat API 流程** - 对话接口时序图
3. **RAG 查询流程** - RAG 操作时序图
4. **Agent 执行流程** - Agent 状态机
5. **项目结构图** - 目录结构展示
6. **API 端点地图** - 思维导图展示所有端点
7. **Docker 部署架构** - 容器化部署结构
8. **依赖关系图** - 技术栈依赖
9. **安全架构** - 安全层级设计
10. **部署流程图** - 部署步骤流程
11. **性能架构** - 性能优化架构
12. **错误处理流程** - 错误处理机制

这些图表可以在支持 Mermaid 的 Markdown 查看器中正确渲染，如：
- GitHub
- GitLab
- VS Code (with Mermaid extension)
- Obsidian
- Typora
- [Mermaid Live Editor](https://mermaid.live)

---

**文档版本**: 1.0
**最后更新**: 2025-11-23
**图表数量**: 12

