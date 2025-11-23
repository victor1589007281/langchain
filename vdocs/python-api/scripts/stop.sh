#!/bin/bash

# LangChain API - 停止脚本

set -e

echo "🛑 停止 LangChain API Service..."

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 停止服务
docker-compose down

echo -e "${GREEN}✅ 服务已停止${NC}"

