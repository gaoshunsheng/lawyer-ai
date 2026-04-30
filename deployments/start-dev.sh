#!/bin/bash

# ==========================================
# 律师AI助手 - 开发环境启动脚本
# ==========================================

set -e

echo "=========================================="
echo "律师AI助手 - 开发环境启动"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装，请先安装Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装，请先安装Docker Compose${NC}"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: .env文件不存在，从.env.example复制...${NC}"
    cp .env.example .env
    echo -e "${GREEN}已创建.env文件，请根据需要修改配置${NC}"
fi

# 停止旧容器
echo -e "${YELLOW}停止旧容器...${NC}"
docker-compose down --remove-orphans

# 构建镜像
echo -e "${YELLOW}构建镜像...${NC}"
docker-compose build

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose up -d postgres redis

# 等待数据库就绪
echo -e "${YELLOW}等待数据库就绪...${NC}"
sleep 10

# 启动Milvus依赖
echo -e "${YELLOW}启动Milvus...${NC}"
docker-compose up -d etcd minio milvus

# 等待Milvus就绪
echo -e "${YELLOW}等待Milvus就绪...${NC}"
sleep 30

# 启动应用服务
echo -e "${YELLOW}启动应用服务...${NC}"
docker-compose up -d lawyer-api ai-service

# 显示服务状态
echo -e "${GREEN}=========================================="
echo "服务启动完成!"
echo "==========================================${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}访问地址:${NC}"
echo "  API文档: http://localhost:8080/api/swagger-ui.html"
echo "  AI服务:  http://localhost:8001/docs"
echo "  MinIO:   http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo -e "${GREEN}命令:${NC}"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
