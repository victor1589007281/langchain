#!/bin/bash

# LangChain API - 日志查看脚本

echo "📋 查看 LangChain API Service 日志..."

# 实时跟踪日志
docker-compose logs -f --tail=100

