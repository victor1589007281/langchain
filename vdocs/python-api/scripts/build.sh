#!/bin/bash

# LangChain API - 构建脚本

set -e

echo "🔨 开始构建 LangChain API Service..."

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose 未安装，请先安装 docker-compose${NC}"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 .env 文件不存在，从 .env.example 创建...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  请编辑 .env 文件，填入你的 API Keys${NC}"
    echo -e "${RED}   特别是 OPENAI_API_KEY 必须配置${NC}"
    exit 1
fi

# 创建必要的目录
echo -e "${BLUE}📁 创建数据目录...${NC}"
mkdir -p data/vector_store data/chroma logs

# 构建 Docker 镜像
echo -e "${BLUE}🐳 构建 Docker 镜像...${NC}"
docker-compose build

echo -e "${GREEN}✅ 构建完成！${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  LangChain API Service 构建成功！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}下一步操作：${NC}"
echo -e "  1. 确认 .env 文件中的配置正确"
echo -e "  2. 运行 ${GREEN}./scripts/deploy.sh${NC} 启动服务"
echo -e "  3. 访问 ${GREEN}http://localhost:8000/docs${NC} 查看 API 文档"
echo ""

