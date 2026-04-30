# 律师AI助手 - 开发进度总结

## 项目概述

本项目是一个面向劳动法律师的专业AI助手系统，包含后端服务和AI服务两个核心模块。

- **后端服务**: Spring Boot 3.2 + Java 17 + PostgreSQL + MyBatis Plus
- **AI服务**: FastAPI + Python + PostgreSQL + Milvus

## 已完成的模块

### 1. 用户认证模块 ✅

**后端服务:**
- 用户实体、租户实体
- JWT认证和授权
- 用户登录、注册、刷新令牌
- 密码修改
- Spring Security配置

**AI服务:**
- 用户模型
- 认证服务
- 认证路由

**文件列表:**
```
lawyer-ai-backend/
├── lawyer-common/src/main/java/com/lawyer/common/
│   ├── enums/UserRole.java
│   ├── utils/JwtUtils.java
│   ├── utils/PasswordUtils.java
│   └── utils/SecurityUtils.java
├── lawyer-service/src/main/java/com/lawyer/service/user/
│   ├── entity/User.java
│   ├── entity/Tenant.java
│   ├── mapper/UserMapper.java
│   ├── mapper/TenantMapper.java
│   └── service/AuthService.java
├── lawyer-api/src/main/java/com/lawyer/api/
│   ├── dto/user/LoginRequest.java
│   ├── dto/user/RegisterRequest.java
│   ├── dto/user/LoginResponse.java
│   ├── dto/user/UserInfo.java
│   ├── dto/user/RefreshTokenRequest.java
│   ├── dto/user/ChangePasswordRequest.java
│   ├── controller/AuthController.java
│   └── security/
│       ├── JwtAuthenticationFilter.java
│       ├── JwtAuthenticationEntryPoint.java
│       ├── JwtAccessDeniedHandler.java
│       └── SecurityConfig.java

lawyer-ai-ai/
├── app/models/user.py
├── app/services/auth_service.py
└── app/api/endpoints/auth.py
```

### 2. 案件管理模块 ✅

**功能:**
- 案件CRUD操作
- 案件时间线管理
- 案件统计
- 证据管理

**文件列表:**
```
lawyer-ai-backend/
├── lawyer-service/src/main/java/com/lawyer/service/case/
│   ├── entity/Case.java
│   ├── entity/Evidence.java
│   ├── mapper/CaseMapper.java
│   ├── mapper/EvidenceMapper.java
│   ├── service/CaseService.java
│   └── service/EvidenceService.java
├── lawyer-api/src/main/java/com/lawyer/api/
│   ├── dto/case/CaseCreateRequest.java
│   ├── dto/case/CaseUpdateRequest.java
│   ├── dto/case/CaseInfo.java
│   ├── dto/case/CaseQueryRequest.java
│   ├── dto/case/CaseStatistics.java
│   ├── dto/case/EvidenceCreateRequest.java
│   ├── dto/case/EvidenceInfo.java
│   ├── controller/CaseController.java
│   └── controller/EvidenceController.java
```

### 3. 文书管理模块 ✅

**功能:**
- 文书CRUD操作
- 文书模板管理
- 基于模板生成文书
- 文书版本管理

**文件列表:**
```
lawyer-ai-backend/
├── lawyer-service/src/main/java/com/lawyer/service/document/
│   ├── entity/Document.java
│   ├── entity/DocumentTemplate.java
│   ├── mapper/DocumentMapper.java
│   ├── mapper/DocumentTemplateMapper.java
│   ├── service/DocumentService.java
│   └── service/TemplateService.java
├── lawyer-api/src/main/java/com/lawyer/api/
│   ├── dto/document/DocumentCreateRequest.java
│   ├── dto/document/DocumentUpdateRequest.java
│   ├── dto/document/DocumentInfo.java
│   ├── dto/document/DocumentQueryRequest.java
│   ├── dto/document/TemplateInfo.java
│   ├── dto/document/DocumentGenerateRequest.java
│   ├── controller/DocumentController.java
│   └── controller/TemplateController.java
```

### 4. 智能咨询模块 ✅

**功能:**
- 聊天会话管理
- 消息历史记录
- AI服务集成
- 模拟法律咨询响应

**文件列表:**
```
lawyer-ai-backend/
├── lawyer-service/src/main/java/com/lawyer/service/chat/
│   ├── client/AiServiceClient.java
│   └── service/ChatService.java
├── lawyer-api/src/main/java/com/lawyer/api/
│   ├── dto/chat/ChatRequest.java
│   ├── dto/chat/ChatResponse.java
│   ├── dto/chat/SessionInfo.java
│   ├── dto/chat/MessageInfo.java
│   └── controller/ChatController.java

lawyer-ai-ai/
├── app/models/user.py (ChatSession, ChatMessage)
├── app/services/chat_service.py
├── app/schemas/chat.py
└── app/api/endpoints/chat.py (完整实现)
```

### 5. 知识库模块 ✅

**功能:**
- 知识条目CRUD
- 知识检索
- 分类管理
- 查看次数统计

**文件列表:**
```
lawyer-ai-backend/
├── lawyer-service/src/main/java/com/lawyer/service/knowledge/
│   ├── entity/Knowledge.java
│   ├── mapper/KnowledgeMapper.java
│   └── service/KnowledgeService.java
├── lawyer-api/src/main/java/com/lawyer/api/
│   ├── dto/knowledge/KnowledgeCreateRequest.java
│   ├── dto/knowledge/KnowledgeInfo.java
│   ├── dto/knowledge/KnowledgeSearchRequest.java
│   ├── dto/knowledge/KnowledgeSearchResult.java
│   └── controller/KnowledgeController.java
```

### 6. 基础设施 ✅

**数据库初始化脚本:**
- `lawyer-ai-backend/sql/init.sql` - 完整的数据库表结构和初始数据

**配置文件:**
- `lawyer-ai-backend/lawyer-api/src/main/resources/application.yml`
- `lawyer-ai-ai/app/core/config.py`

**公共模块:**
- 统一响应格式
- 全局异常处理
- MyBatis Plus配置
- Jackson配置
- HTTP客户端配置

## API端点汇总

### 后端服务 (http://localhost:8080/api)

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | POST /auth/login | 用户登录 |
| 认证 | POST /auth/register | 用户注册 |
| 认证 | POST /auth/refresh | 刷新令牌 |
| 认证 | GET /auth/me | 获取当前用户 |
| 认证 | PUT /auth/password | 修改密码 |
| 案件 | GET/POST /cases | 案件列表/创建 |
| 案件 | GET/PUT/DELETE /cases/{id} | 案件详情/更新/删除 |
| 案件 | GET /cases/statistics | 案件统计 |
| 证据 | GET/POST /evidences | 证据列表/创建 |
| 证据 | GET/PUT/DELETE /evidences/{id} | 证据详情/更新/删除 |
| 文书 | GET/POST /documents | 文书列表/创建 |
| 文书 | GET/PUT/DELETE /documents/{id} | 文书详情/更新/删除 |
| 模板 | GET/POST /templates | 模板列表/创建 |
| 模板 | GET/PUT/DELETE /templates/{id} | 模板详情/更新/删除 |
| 聊天 | POST /chat/message | 发送消息 |
| 聊天 | POST /chat/sessions | 创建会话 |
| 聊天 | GET /chat/sessions | 会话列表 |
| 知识库 | GET/POST /knowledge | 知识列表/创建 |
| 知识库 | GET/PUT/DELETE /knowledge/{id} | 知识详情/更新/删除 |
| 知识库 | GET /knowledge/search | 知识检索 |

### AI服务 (http://localhost:8000/api/v1)

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | POST /auth/login | 用户登录 |
| 认证 | POST /auth/register | 用户注册 |
| 聊天 | POST /chat/message | 发送聊天消息 |
| 聊天 | POST /chat/sessions | 创建会话 |
| 聊天 | GET /chat/sessions/{id}/messages | 获取消息历史 |
| RAG | POST /rag/search | 知识检索 |
| RAG | POST /rag/documents | 添加文档 |
| 文书 | POST /documents/generate | AI生成文书 |
| 计算器 | POST /calculator/illegal-termination | 违法解除赔偿计算 |
| 计算器 | POST /calculator/overtime | 加班费计算 |
| 计算器 | POST /calculator/annual-leave | 年休假计算 |

## 启动说明

### 后端服务
```bash
cd lawyer-ai-backend
mvn clean install
cd lawyer-api
mvn spring-boot:run
```

### AI服务
```bash
cd lawyer-ai-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 数据库初始化
```sql
CREATE DATABASE lawyer_ai;
-- 执行 sql/init.sql
```

## 待完善功能

1. **AI服务增强**
   - 接入真实的LLM API (OpenAI/智谱AI)
   - 实现RAG检索功能
   - 向量数据库数据同步

2. **前端开发**
   - React管理后台
   - 用户界面

3. **测试**
   - 单元测试
   - 集成测试

4. **部署**
   - Docker容器化
   - CI/CD配置

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Spring Boot 3.2 |
| Java版本 | Java 17 |
| ORM | MyBatis Plus 3.5.5 |
| 数据库 | PostgreSQL |
| 缓存 | Redis |
| 认证 | JWT |
| API文档 | Knife4j (OpenAPI 3) |
| AI框架 | FastAPI |
| 向量数据库 | Milvus |
| LLM | OpenAI / 智谱AI |
