#!/bin/bash

# ==========================================
# 律师AI助手 - 停止脚本
# ==========================================

echo "停止所有服务..."
docker-compose --profile production --profile monitoring down

echo "服务已停止"
