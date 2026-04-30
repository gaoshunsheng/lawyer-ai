# 律师AI助手

面向劳动法律师的专业AI助手，聚焦劳动争议案件全流程辅助，提升律师办案效率和文书质量。

## 项目结构

```
lawyer-ai-backend/
├── lawyer-api/              # Spring Boot API模块
│   ├── src/main/java/
│   │   └── com/lawyer/api/
│   │       ├── controller/  # REST控制器
│   │       ├── dto/         # 数据传输对象
│   │       └── security/    # 安全配置
│   └── src/main/resources/
│       └── application.yml  # 应用配置
│
├── lawyer-service/          # 业务服务模块
│   └── src/main/java/
│       └── com/lawyer/service/
│           ├── case/        # 案件服务
│           ├── document/    # 文书服务
│           ├── knowledge/   # 知识库服务
│           ├── ai/          # AI服务集成
│           └── ...          # 其他服务
│
├── lawyer-common/           # 公共模块
│   └── src/main/java/
│       └── com/lawyer/common/
│           ├── config/      # 配置类
│           ├── enums/       # 枚举类
│           ├── utils/       # 工具类
│           └── result/      # 统一响应
│
├── ai-service/              # Python AI服务
│   ├── app/
│   │   ├── api/             # API端点
│   │   ├── services/        # 业务服务
│   │   ├── models/          # 数据模型
│   │   └── core/            # 核心配置
│   ├── tests/               # 测试文件
│   └── main.py              # 入口文件
│
├── sql/                     # 数据库脚本
├── nginx/                   # Nginx配置
├── prometheus/              # Prometheus配置
├── grafana/                 # Grafana配置
├── docker-compose.yml       # Docker编排
├── Dockerfile               # Spring Boot Dockerfile
└── deploy.sh                # 部署脚本
```

## 技术栈

### 后端服务 (Spring Boot)
- Java 17
- Spring Boot 3.2
- MyBatis Plus
- PostgreSQL
- Redis
- JWT认证

### AI服务 (Python)
- Python 3.11
- FastAPI
- Milvus (向量数据库)
- OpenAI / 智谱AI
- LangChain

### 基础设施
- Docker & Docker Compose
- Nginx (反向代理)
- Prometheus (监控)
- Grafana (可视化)

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ 内存
- 20GB+ 磁盘空间

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/lawyer-ai-backend.git
cd lawyer-ai-backend
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置必要的参数
vim .env
```

需要配置的关键参数：
```env
# OpenAI API (或智谱AI)
OPENAI_API_KEY=your-openai-api-key

# JWT密钥 (生产环境必须修改)
JWT_SECRET=your-jwt-secret-key
```

### 3. 启动服务

**开发环境：**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**生产环境：**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. 验证服务

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f lawyer-api
docker-compose logs -f ai-service
```

### 5. 访问服务

| 服务 | 地址 |
|------|------|
| API文档 | http://localhost:8080/api/swagger-ui.html |
| AI服务文档 | http://localhost:8001/docs |
| MinIO控制台 | http://localhost:9001 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

## 功能模块

### 1. 用户管理
- 用户注册/登录
- JWT认证
- 角色权限管理
- 多租户支持

### 2. 案件管理
- 案件CRUD
- 状态流转
- 证据管理
- 时间线管理

### 3. 文书管理
- 文书模板
- AI辅助生成
- 文书版本管理
- 导出Word/PDF

### 4. 智能咨询
- 多轮对话
- 法条引用
- 案例推荐
- 上下文感知

### 5. 知识库
- 向量化存储
- 语义检索
- 法规案例管理

### 6. 赔偿计算器
- 违法解除赔偿
- 加班费计算
- 年休假工资
- 工伤赔偿

### 7. AI分析
- 案件分析
- 胜诉预测
- 风险识别
- 策略建议

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8080/api/swagger-ui.html
- OpenAPI JSON: http://localhost:8080/api/v3/api-docs

## 开发指南

### 本地开发

**Spring Boot:**
```bash
cd lawyer-ai-backend
./mvnw spring-boot:run
```

**AI服务:**
```bash
cd ai-service
pip install -e .
python main.py
```

### 运行测试

**Spring Boot测试:**
```bash
./mvnw test

# 集成测试
./mvnw test -Dtest=*IntegrationTest
```

**AI服务测试:**
```bash
cd ai-service
pytest tests/
pytest tests/ -v --cov=app
```

## 部署说明

### 生产环境检查清单

- [ ] 修改`.env`中的所有敏感配置
- [ ] 配置SSL证书
- [ ] 设置数据库备份
- [ ] 配置日志收集
- [ ] 设置监控告警
- [ ] 配置防火墙规则

### 备份数据

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U postgres lawyer_ai > backup.sql

# 备份MinIO数据
docker-compose exec minio mc mirror local/data backup/
```

### 监控

访问Grafana配置监控面板：
1. 登录 Grafana (http://localhost:3000)
2. 添加 Prometheus 数据源
3. 导入监控面板

## 性能优化

### JVM参数调优
```bash
JAVA_OPTS="-Xms1g -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

### 数据库连接池
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
```

### Redis缓存
```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 600000
```

## 故障排查

### 常见问题

**1. 服务无法启动**
```bash
# 查看日志
docker-compose logs lawyer-api
docker-compose logs ai-service

# 检查端口占用
netstat -tlnp | grep 8080
netstat -tlnp | grep 8001
```

**2. 数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready

# 检查数据库日志
docker-compose logs postgres
```

**3. AI服务响应慢**
- 检查Milvus连接状态
- 查看GPU/CPU使用率
- 调整并发配置

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页: https://github.com/your-repo/lawyer-ai-backend
- 问题反馈: https://github.com/your-repo/lawyer-ai-backend/issues
