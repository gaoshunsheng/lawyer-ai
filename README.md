# 律师AI助手 - 智能法律咨询系统

<div align="center">
  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Java 17](https://img.shields.io/badge/Java-17-orange.svg)](https://www.oracle.com/java/)
[![Vue 3](https://img.shields.io/badge/Vue-3-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-teal.svg)](https://fastapi.tiangolo.com/)

**基于大语言模型和RAG技术的专业法律智能咨询平台**

[项目介绍](#项目介绍) | [功能特性](#功能特性) | [技术架构](#技术架构) | [快速开始](#快速开始) | [部署指南](#部署指南) | [文档](#文档)

</div>

---

## 📋 项目介绍

律师AI助手是一款基于先进大语言模型（LLM）和检索增强生成（RAG）技术的专业级法律咨询服务系统。系统致力于解决普通民众获取专业法律咨询困难、成本高昂的核心痛点，通过智能AI技术提供精准、专业、成本可控的法律咨询服务。

### 🎯 项目目标
- **普惠法律服务**：让普通民众都能获得专业法律咨询
- **智能法律助手**：7×24小时提供准确、及时的法律建议
- **成本大幅降低**：单次服务成本降低90%以上
- **司法效率提升**：为法律工作者提供智能辅助工具

## ✨ 功能特性

### 🔍 智能法律咨询
- **多领域覆盖**：劳动争议、合同纠纷、婚姻家庭、侵权赔偿等
- **RAG增强问答**：基于法律法规和案例的知识检索增强
- **多轮对话**：上下文感知的持续对话能力
- **法律条文引用**：精确引用相关法律条款并解释适用性

### 🧮 专业计算引擎
- **违法解除赔偿计算**：精确计算经济补偿金、赔偿金
- **加班费计算**：区分工作日、休息日、法定节假日加班
- **年休假工资计算**：根据工作年限计算未休年休假工资
- **透明计算过程**：展示完整的计算步骤和法律依据

### 📚 知识管理
- **法律法规库**：实时更新的法律法规数据库
- **案例检索系统**：基于向量检索的相似案例查找
- **文档智能处理**：法律文档上传、解析和知识提取
- **个性化推荐**：基于用户历史的法律建议推荐

### 🛡️ 用户管理
- **多租户支持**：支持律所、企业等多租户使用
- **角色权限控制**：管理员、律师、用户等多级权限
- **对话历史管理**：完整的对话记录和案件关联
- **统计分析**：使用数据统计和业务分析

## 🏗️ 技术架构

### 系统架构图
```
┌─────────────────────────────────────────────────────┐
│                   前端界面 (Vue 3)                   │
└────────────────┬────────────────┬───────────────────┘
                 │                │
    ┌────────────▼─────┐  ┌───────▼──────────┐
    │  主后端服务      │  │  AI服务         │
    │  (Java Spring)   │  │  (Python FastAPI) │
    └────────────┬─────┘  └───────┬──────────┘
                 │                │
    ┌────────────▼────────────────▼───────┐
    │        数据库 & 向量存储            │
    │  PostgreSQL + Milvus + Elasticsearch │
    └─────────────────────────────────────┘
```

### 核心技术栈
- **后端服务**：Java 17 + Spring Boot 3 + MyBatis Plus
- **AI服务**：Python 3.11 + FastAPI + LangChain + OpenAI API
- **前端界面**：Vue 3 + TypeScript + Vite + Element Plus
- **数据库**：PostgreSQL + Redis + Milvus (向量数据库)
- **检索系统**：Elasticsearch + 语义向量检索
- **部署运维**：Docker + Docker Compose + Nginx
- **监控系统**：Prometheus + Grafana

### 创新技术
- **长链推理架构**：四级推理链条确保专业准确性
- **多Agent协作**：五类专业Agent协同处理复杂法律问题
- **混合检索策略**：向量检索 + 关键词检索 + 权威性排序
- **可解释AI设计**：推理过程透明，证据链完整

## 🚀 快速开始

### 环境要求
- Docker 20.10+ 和 Docker Compose 2.0+
- Java 17 或更高版本
- Python 3.11+ 和 Node.js 18+

### 一键部署（开发环境）
```bash
# 克隆项目
git clone https://github.com/gaoshunsheng/lawyer-ai.git
cd lawyer-ai

# 启动所有服务
cd deployments
./start-dev.sh

# 访问服务
# 前端界面：http://localhost:3000
# 后端API：http://localhost:8080
# AI服务：http://localhost:8000
# API文档：http://localhost:8000/docs
```

### 分步启动
```bash
# 1. 启动数据库和中间件
docker-compose up -d postgres redis milvus elasticsearch

# 2. 启动后端服务
cd backend
mvn spring-boot:run

# 3. 启动AI服务
cd ../ai-service
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. 启动前端服务
cd ../frontend
npm install
npm run dev
```

## 📁 项目结构

```
lawyer-ai/
├── backend/                    # 主后端服务 (Java Spring Boot)
│   ├── lawyer-api/            # API接口服务
│   ├── lawyer-common/         # 公共模块
│   ├── lawyer-service/        # 业务服务
│   └── pom.xml               # Maven配置
├── ai-service/                # AI微服务 (Python FastAPI)
│   ├── app/                  # 应用代码
│   │   ├── api/             # API端点
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic模型
│   │   └── services/        # 业务服务
│   ├── requirements.txt      # Python依赖
│   └── README.md            # AI服务文档
├── frontend/                 # 前端应用 (Vue 3)
│   ├── src/                 # 源代码
│   ├── package.json         # 依赖配置
│   └── vite.config.ts       # 构建配置
├── deployments/              # 部署配置
│   ├── docker-compose.yml   # Docker编排
│   ├── Dockerfile          # Docker镜像
│   ├── scripts/            # 部署脚本
│   ├── configs/            # 配置文件
│   ├── monitoring/         # 监控配置
│   └── sql/               # 数据库脚本
├── docs/                    # 项目文档
│   ├── ARCHITECTURE.md     # 架构设计
│   ├── API.md             # API接口文档
│   ├── DATABASE.md        # 数据库设计
│   ├── PRD.md            # 产品需求文档
│   └── TESTCASE.md       # 测试用例
└── README.md               # 项目总说明
```

## 📊 部署指南

### 生产环境部署
```bash
# 1. 环境准备
cp backend/.env.example backend/.env
cp ai-service/.env.example ai-service/.env

# 2. 修改配置文件
# 编辑backend/.env 和 ai-service/.env中的配置

# 3. 构建并启动
cd deployments
docker-compose up -d --build

# 4. 初始化数据库
./scripts/init-database.sh
```

### 配置说明
- **后端配置**：编辑 `backend/.env` 配置数据库、Redis等
- **AI服务配置**：编辑 `ai-service/.env` 配置API密钥、模型等
- **前端配置**：编辑 `frontend/.env.production` 配置API地址
- **Docker配置**：编辑 `deployments/docker-compose.yml` 调整资源限制

## 📖 文档

详细文档请查看 [docs/](docs/) 目录：

- [系统架构设计](docs/ARCHITECTURE.md) - 详细的技术架构和设计决策
- [API接口文档](docs/API.md) - 完整的API接口说明和示例
- [数据库设计](docs/DATABASE.md) - 数据库表结构和关系设计
- [产品需求文档](docs/PRD.md) - 产品功能需求和业务逻辑
- [测试用例](docs/TESTCASE.md) - 功能测试和集成测试用例

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

### 开发流程
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有贡献者和使用者
- 感谢开源社区提供的优秀工具和库
- 感谢小米MIMO平台提供的技术支持

## 📞 联系方式

- 项目负责人：Gaoshunsheng
- GitHub：[@gaoshunsheng](https://github.com/gaoshunsheng)
- 邮箱：[您的邮箱]

---

<div align="center">
  
**⭐ 如果这个项目对您有帮助，请给我们一个星星！** ⭐

</div>