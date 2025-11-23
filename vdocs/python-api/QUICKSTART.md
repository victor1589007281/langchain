# 🚀 快速开始指南

## 5 分钟部署 LangChain API Service

### 第一步：准备 API Key

你需要一个 OpenAI API Key。访问 https://platform.openai.com/api-keys 获取。

### 第二步：一键启动

```bash
# 克隆或进入项目目录
cd vdocs/python-api

# 运行快速启动脚本
make quick-start
```

这将自动：
1. ✅ 构建 Docker 镜像
2. ✅ 创建 .env 文件
3. ✅ 启动服务

### 第三步：配置 API Key

编辑 `.env` 文件：

```bash
vim .env
```

修改以下行：

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

保存后重启服务：

```bash
make restart
```

### 第四步：测试 API

访问 API 文档：http://localhost:8000/docs

或使用 curl 测试：

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试对话
curl -X POST "http://localhost:8000/api/v1/chat/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 常用命令

```bash
make deploy      # 启动服务
make stop        # 停止服务
make restart     # 重启服务
make logs        # 查看日志
make status      # 查看状态
make clean       # 清理所有数据
```

## 🎯 API 端点速查

| 端点 | 功能 | 示例 |
|------|------|------|
| `/api/v1/chat/invoke` | 对话 | `{"messages": [{"role": "user", "content": "Hi"}]}` |
| `/api/v1/rag/index` | 创建索引 | `{"documents": [...], "collection_name": "docs"}` |
| `/api/v1/rag/query` | RAG 查询 | `{"query": "...", "collection_name": "docs"}` |
| `/api/v1/agent/execute` | Agent | `{"task": "...", "tools": ["calculator"]}` |
| `/api/v1/embeddings/embed` | 向量化 | `{"texts": ["text1", "text2"]}` |

## 🔥 实战示例

### 示例 1: 对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "什么是 LangChain？"}
    ],
    "system_message": "你是一个AI专家"
  }'
```

### 示例 2: RAG（检索增强生成）

```bash
# 1. 创建索引
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"content": "LangChain 是一个用于构建 LLM 应用的框架", "metadata": {"source": "doc1"}},
      {"content": "它提供了丰富的工具和组件", "metadata": {"source": "doc2"}}
    ],
    "collection_name": "my_knowledge"
  }'

# 2. 查询
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "LangChain 有什么用？",
    "collection_name": "my_knowledge",
    "k": 2
  }'
```

### 示例 3: Agent（智能代理）

```bash
curl -X POST "http://localhost:8000/api/v1/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "计算 123 * 456，然后告诉我现在几点",
    "tools": ["calculator", "get_current_time"],
    "max_iterations": 5
  }'
```

### 示例 4: 文本向量化

```bash
curl -X POST "http://localhost:8000/api/v1/embeddings/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["机器学习", "深度学习", "人工智能"],
    "model": "text-embedding-ada-002"
  }'
```

## 🐳 Docker 命令速查

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec langchain-api bash

# 重启容器
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除所有数据
docker-compose down -v
```

## 📊 监控

### 健康检查

```bash
curl http://localhost:8000/health
```

### 查看日志

```bash
# 实时日志
make logs

# 或
docker-compose logs -f

# 查看最近 100 行
docker-compose logs --tail=100
```

### 查看资源使用

```bash
docker stats langchain-api
```

## ❓ 常见问题

### Q: 服务启动失败？

**A**: 检查以下内容：
1. Docker 是否运行？`docker ps`
2. 端口 8000 是否被占用？`lsof -i :8000`
3. API Key 是否正确配置？检查 `.env` 文件
4. 查看日志：`make logs`

### Q: API 返回 500 错误？

**A**: 可能原因：
1. API Key 无效或额度不足
2. 网络连接问题
3. 查看详细日志：`docker-compose logs`

### Q: RAG 查询没有结果？

**A**: 确保：
1. 先创建索引：`POST /api/v1/rag/index`
2. collection_name 一致
3. 文档内容相关

### Q: 如何使用其他模型？

**A**: 在请求中指定：

```json
{
  "messages": [...],
  "config": {
    "model": "gpt-4",
    "temperature": 0.7
  }
}
```

### Q: 如何持久化数据？

**A**: 数据自动保存在：
- 向量数据：`./data/chroma/`
- 日志：`./logs/`

这些目录通过 Docker Volume 挂载，重启容器不会丢失。

## 🔒 安全建议

1. **不要提交 .env 文件**到 Git
2. **使用环境变量**管理敏感信息
3. **定期更新**依赖包
4. **生产环境**启用认证
5. **限制**CORS 允许的来源

## 🚀 进阶使用

### 使用 Python 客户端

```python
import requests

# 对话
response = requests.post(
    "http://localhost:8000/api/v1/chat/invoke",
    json={
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)
print(response.json())
```

### 使用 JavaScript 客户端

```javascript
const response = await fetch('http://localhost:8000/api/v1/chat/invoke', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Hello!' }
    ]
  })
});

const data = await response.json();
console.log(data);
```

## 📚 更多资源

- **完整文档**: [README.md](README.md)
- **架构说明**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API 文档**: http://localhost:8000/docs
- **LangChain 文档**: https://python.langchain.com/

## 💡 提示

- 使用 **Swagger UI** (http://localhost:8000/docs) 交互式测试 API
- 查看 **示例** 端点获取更多配置示例
- 关注 **日志** 了解执行详情
- 使用 **健康检查** 端点监控服务状态

---

🎉 **开始使用 LangChain API Service！**

有问题？查看 [README.md](README.md) 或提交 Issue。

