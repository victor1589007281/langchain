.PHONY: help build deploy stop logs clean install dev test

# 默认目标
.DEFAULT_GOAL := help

help: ## 显示帮助信息
	@echo "LangChain API Service - 可用命令："
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

build: ## 构建 Docker 镜像
	@echo "🔨 构建 Docker 镜像..."
	@./scripts/build.sh

deploy: ## 部署服务
	@echo "🚀 部署服务..."
	@./scripts/deploy.sh

stop: ## 停止服务
	@echo "🛑 停止服务..."
	@./scripts/stop.sh

logs: ## 查看日志
	@./scripts/logs.sh

restart: stop deploy ## 重启服务

clean: ## 清理生成的文件和容器
	@echo "🧹 清理..."
	@docker-compose down -v 2>/dev/null || true
	@rm -rf data/ logs/ __pycache__/ .pytest_cache/ 2>/dev/null || true
	@echo "✅ 清理完成"

install: ## 本地安装依赖（开发模式）
	@echo "📦 安装依赖..."
	@pip install -r requirements.txt

dev: ## 本地开发模式运行
	@echo "🔧 启动开发模式..."
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## 运行测试
	@echo "🧪 运行测试..."
	@pytest tests/ -v

lint: ## 代码检查
	@echo "🔍 代码检查..."
	@python -m black app/ --check
	@python -m isort app/ --check-only
	@python -m flake8 app/

format: ## 格式化代码
	@echo "✨ 格式化代码..."
	@python -m black app/
	@python -m isort app/

status: ## 查看服务状态
	@docker-compose ps

shell: ## 进入容器 Shell
	@docker-compose exec langchain-api /bin/bash

ps: ## 显示容器进程
	@docker ps | grep langchain-api || echo "服务未运行"

quick-start: build deploy ## 快速启动（构建 + 部署）
	@echo ""
	@echo "✅ 服务已启动！"
	@echo "📖 API 文档: http://localhost:8000/docs"

