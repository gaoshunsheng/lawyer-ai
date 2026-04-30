#!/bin/bash

# ==========================================
# 律师AI助手 - 生产环境部署脚本
# ==========================================

set -e

echo "=========================================="
echo "律师AI助手 - 生产环境部署"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查环境变量
if [ ! -f .env ]; then
    echo -e "${RED}错误: .env文件不存在，请复制.env.example并配置${NC}"
    exit 1
fi

# 检查必要的配置
source .env

if [ -z "$OPENAI_API_KEY" ] && [ -z "$ZHIPU_API_KEY" ]; then
    echo -e "${RED}错误: 请配置OPENAI_API_KEY或ZHIPU_API_KEY${NC}"
    exit 1
fi

if [ "$JWT_SECRET" == "lawyer-ai-jwt-secret-key-change-in-production" ]; then
    echo -e "${YELLOW}警告: JWT_SECRET使用默认值，生产环境请修改!${NC}"
fi

# 拉取最新代码
echo -e "${YELLOW}拉取最新代码...${NC}"
git pull

# 停止旧容器
echo -e "${YELLOW}停止旧容器...${NC}"
docker-compose --profile production down --remove-orphans

# 清理旧镜像
echo -e "${YELLOW}清理旧镜像...${NC}"
docker image prune -f

# 构建镜像
echo -e "${YELLOW}构建镜像...${NC}"
docker-compose build --no-cache

# 数据库迁移备份
echo -e "${YELLOW}备份数据库...${NC}"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backups/$BACKUP_FILE 2>/dev/null || echo "跳过备份"

# 启动基础设施
echo -e "${YELLOW}启动基础设施...${NC}"
docker-compose up -d postgres redis etcd minio milvus

# 等待服务就绪
echo -e "${YELLOW}等待服务就绪...${NC}"
sleep 30

# 运行数据库迁移
echo -e "${YELLOW}运行数据库迁移...${NC}"
docker-compose exec -T lawyer-api java -jar app.jar --spring.jpa.hibernate.ddl-auto=update || true

# 启动应用服务
echo -e "${YELLOW}启动应用服务...${NC}"
docker-compose --profile production up -d lawyer-api ai-service nginx

# 健康检查
echo -e "${YELLOW}健康检查...${NC}"
sleep 10

# 检查API服务
if curl -sf http://localhost:8080/actuator/health > /dev/null; then
    echo -e "${GREEN}✓ API服务健康${NC}"
else
    echo -e "${RED}✗ API服务不健康${NC}"
fi

# 检查AI服务
if curl -sf http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✓ AI服务健康${NC}"
else
    echo -e "${RED}✗ AI服务不健康${NC}"
fi

# 显示服务状态
echo -e "${GREEN}=========================================="
echo "部署完成!"
echo "==========================================${NC}"
docker-compose --profile production ps

echo ""
echo -e "${GREEN}访问地址:${NC}"
echo "  应用入口: http://localhost"
echo "  API文档:  http://localhost/api/swagger-ui.html"
echo "  AI文档:   http://localhost/ai/docs"
echo ""
echo -e "${GREEN}监控:${NC}"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana:    http://localhost:3000"
