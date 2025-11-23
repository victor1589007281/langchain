#!/bin/bash

# LangChain API - 部署脚本

set -e

echo "🚀 部署 LangChain API Service..."

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env 文件不存在${NC}"
    echo -e "${YELLOW}请先运行 ./scripts/build.sh 构建项目${NC}"
    exit 1
fi

# 检查 OPENAI_API_KEY
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${YELLOW}⚠️  警告: OPENAI_API_KEY 可能未正确配置${NC}"
    echo -e "${YELLOW}   请确保在 .env 文件中设置了有效的 OpenAI API Key${NC}"
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 停止旧容器
echo -e "${BLUE}🛑 停止旧容器...${NC}"
docker-compose down 2>/dev/null || true

# 启动服务
echo -e "${BLUE}🐳 启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${BLUE}⏳ 等待服务启动...${NC}"
sleep 5

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  LangChain API Service 已启动！${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}📍 访问地址：${NC}"
    echo -e "   • API 文档（Swagger）: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "   • API 文档（ReDoc）:   ${GREEN}http://localhost:8000/redoc${NC}"
    echo -e "   • 健康检查:           ${GREEN}http://localhost:8000/health${NC}"
    echo ""
    echo -e "${BLUE}📊 查看日志：${NC}"
    echo -e "   docker-compose logs -f"
    echo ""
    echo -e "${BLUE}🛑 停止服务：${NC}"
    echo -e "   docker-compose down"
    echo ""
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo -e "${YELLOW}查看日志：${NC}"
    docker-compose logs
    exit 1
fi

