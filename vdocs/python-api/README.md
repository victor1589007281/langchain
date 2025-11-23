# 🦜 LangChain RESTful API Service

基于 FastAPI 的 LangChain 完整功能封装，提供易用的 RESTful API 接口。

## ✨ 特性

- 💬 **Chat API** - 完整的对话和聊天功能（支持流式输出）
- 📚 **RAG API** - 检索增强生成（文档索引、向量搜索、智能问答）
- 🤖 **Agent API** - 智能代理（工具调用、多步推理）
- 🔢 **Embeddings API** - 文本向量化和相似度计算
- 🛠️ **Tools API** - 工具管理和直接调用
- ⛓️ **Chains API** - 灵活的链式操作（顺序、并行、条件）
- 🐳 **Docker 支持** - 完整的容器化部署方案
- 📖 **自动文档** - Swagger UI 和 ReDoc 自动生成
- 🔒 **生产就绪** - 日志、健康检查、错误处理

## 📋 目录

- [快速开始](#快速开始)
- [API 文档](#api-文档)
- [部署指南](#部署指南)
- [API 使用示例](#api-使用示例)
- [配置说明](#配置说明)
- [开发指南](#开发指南)

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- OpenAI API Key（必需）

### 一键部署

```bash
# 1. 进入项目目录
cd vdocs/python-api

# 2. 构建 Docker 镜像
./scripts/build.sh

# 3. 编辑 .env 文件，填入你的 API Keys
vim .env
# 至少需要设置 OPENAI_API_KEY=your-key-here

# 4. 启动服务
./scripts/deploy.sh
```

服务启动后，访问：
- **API 文档（Swagger）**: http://localhost:8000/docs
- **API 文档（ReDoc）**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 本地开发模式

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制并编辑环境变量
cp .env.example .env
vim .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API 文档

### 1. Chat API - 对话接口

#### 1.1 同步对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "什么是 LangChain？"}
    ],
    "system_message": "你是一个AI助手"
  }'
```

#### 1.2 流式对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "讲一个故事"}
    ]
  }'
```

### 2. RAG API - 检索增强生成

#### 2.1 创建索引

```bash
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "LangChain 是一个用于构建 LLM 应用的框架。",
        "metadata": {"source": "doc1"}
      },
      {
        "content": "它提供了工具、组件和接口来简化 AI 应用开发。",
        "metadata": {"source": "doc2"}
      }
    ],
    "collection_name": "my_docs",
    "chunk_size": 1000,
    "chunk_overlap": 200
  }'
```

#### 2.2 查询

```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "LangChain 是什么？",
    "collection_name": "my_docs",
    "k": 3
  }'
```

### 3. Agent API - 智能代理

```bash
curl -X POST "http://localhost:8000/api/v1/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "计算 25 * 4，然后告诉我当前时间",
    "tools": ["calculator", "get_current_time"],
    "max_iterations": 5
  }'
```

### 4. Embeddings API - 文本向量化

#### 4.1 生成嵌入

```bash
curl -X POST "http://localhost:8000/api/v1/embeddings/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello, world!", "LangChain is awesome"],
    "model": "text-embedding-ada-002"
  }'
```

#### 4.2 计算相似度

```bash
curl -X POST "http://localhost:8000/api/v1/embeddings/similarity" \
  -H "Content-Type: application/json" \
  -d '{
    "text1": "机器学习",
    "text2": "人工智能"
  }'
```

### 5. Tools API - 工具管理

#### 5.1 列出工具

```bash
curl -X GET "http://localhost:8000/api/v1/tools/list"
```

#### 5.2 调用工具

```bash
curl -X POST "http://localhost:8000/api/v1/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculator",
    "arguments": {"expression": "10 + 5"}
  }'
```

### 6. Chains API - 链式操作

```bash
curl -X POST "http://localhost:8000/api/v1/chains/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "chain_type": "simple",
    "steps": [
      {
        "type": "prompt",
        "config": {"template": "请回答：{input}"}
      }
    ],
    "input": "什么是 AI？"
  }'
```

## 🐳 部署指南

### Docker Compose 部署（推荐）

```bash
# 构建和启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

### Docker 直接运行

```bash
# 构建镜像
docker build -t langchain-api .

# 运行容器
docker run -d \
  --name langchain-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key-here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  langchain-api
```

### Kubernetes 部署

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langchain-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: langchain-api
  template:
    metadata:
      labels:
        app: langchain-api
    spec:
      containers:
      - name: langchain-api
        image: langchain-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
---
apiVersion: v1
kind: Service
metadata:
  name: langchain-api
spec:
  selector:
    app: langchain-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | ✅ |
| `DEFAULT_MODEL` | 默认模型 | gpt-3.5-turbo | ❌ |
| `DEFAULT_TEMPERATURE` | 默认温度 | 0.7 | ❌ |
| `HOST` | 服务主机 | 0.0.0.0 | ❌ |
| `PORT` | 服务端口 | 8000 | ❌ |
| `LOG_LEVEL` | 日志级别 | INFO | ❌ |
| `DEBUG` | 调试模式 | false | ❌ |

完整配置请参考 `.env.example`。

## 🛠️ 管理脚本

项目提供了便捷的管理脚本：

| 脚本 | 说明 |
|------|------|
| `scripts/build.sh` | 构建 Docker 镜像 |
| `scripts/deploy.sh` | 部署服务 |
| `scripts/stop.sh` | 停止服务 |
| `scripts/logs.sh` | 查看日志 |

所有脚本都有可执行权限并包含详细的状态提示。

## 📊 项目结构

```
python-api/
├── app/                        # 应用代码
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   └── logging_config.py  # 日志配置
│   ├── models/                 # 数据模型
│   │   └── schemas.py          # Pydantic 模型
│   └── api/                    # API 端点
│       ├── chat.py             # Chat API
│       ├── rag.py              # RAG API
│       ├── agent.py            # Agent API
│       ├── embeddings.py       # Embeddings API
│       ├── tools.py            # Tools API
│       └── chains.py           # Chains API
├── scripts/                    # 部署脚本
│   ├── build.sh               # 构建脚本
│   ├── deploy.sh              # 部署脚本
│   ├── stop.sh                # 停止脚本
│   └── logs.sh                # 日志查看
├── data/                       # 数据目录（持久化）
├── logs/                       # 日志目录
├── Dockerfile                  # Docker 配置
├── docker-compose.yml         # Docker Compose 配置
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量示例
└── README.md                  # 本文件
```

## 🔧 开发指南

### 添加新的 API 端点

1. 在 `app/api/` 下创建新的路由文件
2. 在 `app/models/schemas.py` 中定义数据模型
3. 在 `app/main.py` 中注册路由

示例：

```python
# app/api/my_feature.py
from fastapi import APIRouter
from app.models.schemas import MyRequest, MyResponse

router = APIRouter()

@router.post("/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest):
    # 实现逻辑
    return MyResponse(result="success")
```

```python
# app/main.py
from app.api import my_feature

app.include_router(
    my_feature.router,
    prefix="/api/v1/my-feature",
    tags=["My Feature"]
)
```

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest tests/
```

## 📝 API 响应格式

### 成功响应

```json
{
  "message": "Success message",
  "data": { ... }
}
```

### 错误响应

```json
{
  "detail": "Error message"
}
```

## 🔍 监控和日志

### 查看日志

```bash
# Docker Compose
./scripts/logs.sh

# 或直接使用
docker-compose logs -f

# 查看日志文件
tail -f logs/app.log
```

### 健康检查

```bash
curl http://localhost:8000/health
```

返回：

```json
{
  "status": "healthy",
  "service": "LangChain API Service",
  "version": "1.0.0",
  "environment": "production"
}
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)

## 📞 支持

如有问题，请：
1. 查看文档：http://localhost:8000/docs
2. 查看日志：`./scripts/logs.sh`
3. 提交 Issue

---

**快速开始命令**：

```bash
./scripts/build.sh && ./scripts/deploy.sh
```

**访问文档**：http://localhost:8000/docs

🎉 **享受使用 LangChain API Service！**

