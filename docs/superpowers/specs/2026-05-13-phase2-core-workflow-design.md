# Phase 2 设计文档：核心办案流程

**Goal:** 交付完整办案流程（创建案件→收集证据→生成文书→AI分析→合同审查→结案），实现数据反馈飞轮闭环。

**Architecture:** 在 Phase 1 基础上扩展。后端新增案件/文书/证据模型和 API，LangGraph 新增 Document/Analysis/Review 三个 Agent。前端新增案件管理、文书中心、合同审查、反馈看板页面。

**Tech Stack:** 沿用 Phase 1 技术栈：Next.js 14, FastAPI, SQLAlchemy 2.x (async), pgvector, LangGraph 1.0, 智谱AI GLM-5.1/GLM-5-Turbo, Supabase

**Implementation Strategy:** 按 PRD 模块顺序推进：案件管理→文书中心→AI增强→知识库增强→合同审查→反馈飞轮。全部完成后统一部署。

---

## Module 1: 案件管理

### 数据模型

**`cases` 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| case_number | VARCHAR(100) | 自动生成案号，如 "LD-2026-0001" |
| title | VARCHAR(200) | 案件标题 |
| case_type | VARCHAR(50) | 7类枚举：labor_contract/wage/injury/social_insurance/termination/discrimination/other |
| status | VARCHAR(20) | 8态：pending/in_progress/filed/hearing/mediating/closed/archived/cancelled |
| plaintiff | JSONB | 原告信息（姓名/身份证/联系方式） |
| defendant | JSONB | 被告信息 |
| claim_amount | NUMERIC(12,2) | 标的金额 |
| dispute_focus | ARRAY(TEXT) | 争议焦点列表 |
| lawyer_id | UUID FK → users | 承办律师 |
| assistant_id | UUID FK → users | 律师助理（可选） |
| tenant_id | UUID FK → tenants | 所属律所 |
| gantt_data | JSONB | 甘特图节点数据（Phase 3 使用） |
| ai_analysis | JSONB | AI分析结果缓存 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

**`evidences` 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| case_id | UUID FK → cases | 所属案件 |
| tenant_id | UUID FK → tenants | 所属律所 |
| title | VARCHAR(200) | 证据名称 |
| evidence_type | VARCHAR(50) | 枚举：contract/chat_record/photo/video/audio/document/other |
| file_url | VARCHAR(500) | Supabase Storage URL |
| file_size | BIGINT | 文件大小（字节） |
| file_type | VARCHAR(50) | MIME 类型 |
| description | TEXT | 证据说明 |
| sort_order | INTEGER | 排序序号 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

**`case_timelines` 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| case_id | UUID FK → cases | 所属案件 |
| event_type | VARCHAR(20) | milestone/task/deadline/note |
| title | VARCHAR(200) | 事件标题 |
| description | TEXT | 事件描述 |
| event_date | DATE | 事件日期 |
| created_by | UUID FK → users | 创建人 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

### API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/cases` | GET | 案件列表（分页+状态/类型/律师筛选） |
| `/api/v1/cases` | POST | 创建案件 |
| `/api/v1/cases/{id}` | GET | 案件详情 |
| `/api/v1/cases/{id}` | PUT | 更新案件 |
| `/api/v1/cases/{id}/status` | PATCH | 更新案件状态 |
| `/api/v1/cases/{id}/evidences` | GET | 证据列表 |
| `/api/v1/cases/{id}/evidences` | POST | 上传证据（multipart） |
| `/api/v1/cases/{id}/evidences/{eid}` | PUT | 更新证据 |
| `/api/v1/cases/{id}/evidences/{eid}` | DELETE | 删除证据 |
| `/api/v1/cases/{id}/timeline` | GET | 时间线事件列表 |
| `/api/v1/cases/{id}/timeline` | POST | 添加时间线事件 |
| `/api/v1/cases/{id}/timeline/{tid}` | PUT | 更新时间线事件 |
| `/api/v1/cases/{id}/timeline/{tid}` | DELETE | 删除时间线事件 |

### 前端页面

- `frontend/src/app/(dashboard)/cases/page.tsx` - 案件列表（筛选+搜索+分页）
- `frontend/src/app/(dashboard)/cases/[id]/page.tsx` - 案件详情（多Tab：信息/时间线/证据/文书/AI分析）
- `frontend/src/app/(dashboard)/cases/new/page.tsx` - 创建案件表单

### 文件结构

```
backend/app/models/case.py              # Case, Evidence, CaseTimeline
backend/app/schemas/case.py             # 请求/响应模型
backend/app/services/case_service.py    # 业务逻辑
backend/app/api/v1/cases.py             # API路由

frontend/src/app/(dashboard)/cases/page.tsx
frontend/src/app/(dashboard)/cases/[id]/page.tsx
frontend/src/app/(dashboard)/cases/new/page.tsx
```

---

## Module 2: 文书中心

### 数据模型

**`document_templates` 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| name | VARCHAR(200) | 模板名称 |
| doc_type | VARCHAR(50) | 文书类型枚举 |
| content_template | TEXT | 含 {{变量}} 占位符的模板文本 |
| variables_schema | JSONB | 变量定义：名称/类型/必填/默认值 |
| category | VARCHAR(50) | 分类：申请类/起诉类/答辩类/函件类/协议类/证据类/代理类/通知类 |
| sort_order | INTEGER | 排序 |
| is_system | BOOLEAN | 系统内置模板不可删 |
| tenant_id | UUID | NULL=系统模板 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

**`documents` 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| case_id | UUID FK → cases | 关联案件（可选） |
| tenant_id | UUID FK → tenants | 所属律所 |
| user_id | UUID FK → users | 创建人 |
| title | VARCHAR(200) | 文书标题 |
| doc_type | VARCHAR(50) | 文书类型 |
| template_id | UUID FK → document_templates | 使用的模板 |
| content | JSONB | 富文本结构化内容 |
| variables | JSONB | 已填充的变量值 |
| status | VARCHAR(20) | draft/generating/completed/exported |
| version | INTEGER | 版本号 |
| parent_id | UUID FK → documents | 上一版本 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

### 初始模板数据（10个）

| 模板名称 | doc_type | 优先级 |
|----------|----------|--------|
| 劳动争议仲裁申请书 | arbitration_application | P0 |
| 民事起诉状（劳动争议） | complaint | P0 |
| 民事答辩状 | defense_letter | P0 |
| 律师函 | lawyer_letter | P0 |
| 和解协议书 | settlement_agreement | P0 |
| 证据清单 | evidence_list | P0 |
| 代理词 | representation_letter | P1 |
| 强制执行申请书 | enforcement_application | P1 |
| 劳动合同 | labor_contract | P2 |
| 解除劳动合同通知书 | termination_notice | P2 |

### API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/document-templates` | GET | 模板列表（按分类） |
| `/api/v1/documents` | GET | 文书列表（分页+案件筛选） |
| `/api/v1/documents` | POST | 创建文书（选模板+填变量） |
| `/api/v1/documents/{id}` | GET | 文书详情 |
| `/api/v1/documents/{id}` | PUT | 更新文书内容 |
| `/api/v1/documents/{id}/generate` | POST | AI生成文书（SSE流式） |
| `/api/v1/documents/{id}/export` | POST | 导出为 Word/PDF |

### 前端页面

- `frontend/src/app/(dashboard)/documents/page.tsx` - 文书列表
- `frontend/src/app/(dashboard)/documents/templates/page.tsx` - 模板库浏览
- `frontend/src/app/(dashboard)/documents/[id]/page.tsx` - 文书编辑器
- `frontend/src/app/(dashboard)/documents/new/page.tsx` - 创建文书（选模板→填变量→生成）

---

## Module 3: AI增强

### 新增 LangGraph Agent

在现有 Router Agent 基础上扩展路由，新增 3 个专业 Agent：

**Document Agent（文书生成）**
- 输入：案件信息 + 文书类型 + 用户要求
- 处理：RAG 检索相关法条 → 按模板结构生成各段落
- 输出：结构化文书内容
- 模型：GLM-5.1

**Analysis Agent（案件分析）**
- 输入：案件材料（案情+证据+时间线）
- 处理：分析优劣势、识别风险点、引用法条和案例
- 输出：JSONB（strengths/weaknesses/risks/strategy/win_prediction）
- 模型：GLM-5-Turbo

**Review Agent（合同审查）**
- 输入：合同全文（OCR 提取）
- 处理：5维度审查
- 输出：审查报告（评分 + 风险条目 + 修改建议）
- 模型：GLM-5.1

### LangGraph 路由扩展

```
Router Agent（GLM-4-Flash）
├── consult → Consult Agent（已有）
├── document → Document Agent（新增）
├── review → Review Agent（新增）
└── analysis → Analysis Agent（新增）
```

### 合同审查工作流

```
上传合同 → Supabase Storage → OCR/文本提取 → Review Agent 5维度审查 → 生成报告
                                                     ├── 合规性检查（法定条款完整性）
                                                     ├── 风险条款识别（高/中/低分级）
                                                     ├── 法规适用性（过期法规标注）
                                                     ├── 完整性评估（缺失条款列出）
                                                     └── 金额验证（低于法定线标注）
```

### API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/cases/{id}/analyze` | POST | AI案件分析 |
| `/api/v1/documents/{id}/generate` | POST | AI文书生成（SSE流式） |
| `/api/v1/documents/{id}/smart-suggest` | POST | 智能建议（法条引用校验） |
| `/api/v1/contracts/review` | POST | 合同审查（上传→分析） |
| `/api/v1/contracts/{id}/report` | GET | 获取审查报告 |

### 前端页面

- `frontend/src/app/(dashboard)/contracts/page.tsx` - 合同审查（上传+结果展示）
- 案件详情页增加 AI分析 Tab
- 文书编辑器增加 AI生成按钮

---

## Module 4: 知识库增强

### 新增数据模型

**`favorites` 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| user_id | UUID FK → users | 用户 |
| target_type | VARCHAR(20) | law/case/article |
| target_id | UUID | 目标 ID |
| notes | TEXT | 用户笔记 |
| created_at | TIMESTAMPTZ | 创建时间 |

### API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/favorites` | GET | 收藏列表（按类型筛选） |
| `/api/v1/favorites` | POST | 添加收藏 |
| `/api/v1/favorites/{id}` | DELETE | 取消收藏 |
| `/api/v1/favorites/{id}` | PUT | 更新笔记 |
| `/api/v1/knowledge/laws/{id}/interpret` | POST | AI法规解读（SSE流式） |
| `/api/v1/knowledge/import` | POST | 批量导入法规（JSON） |

### 前端

- 知识库页面增加收藏按钮和收藏列表
- 法规详情页增加"AI解读"按钮
- 管理员批量导入功能

---

## Module 5: 数据反馈飞轮

### 已有基础

Phase 1 已实现 `response_feedbacks` 表和 `/api/v1/feedback` API。

### Phase 2 补充

**前端评价组件**：每条 AI 回复下方展示：
- 👍👎 总体评价（必填）
- 3 个星级维度：法条准确性 / 分析深度 / 实用价值（1-5星）
- 文字反馈（最多500字）

**反馈聚合看板**：
- 日/周/月维度统计
- 满意度趋势图
- 差评率预警（>15% 标红）

### API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/feedback/stats` | GET | 反馈聚合统计 |
| `/api/v1/feedback/trends` | GET | 满意度趋势数据 |

### 前端页面

- Chat 页面集成评价组件
- `frontend/src/app/(dashboard)/feedback/page.tsx` - 反馈看板（管理员）

---

## Database Migration

Phase 2 新增 6 张表，需要 1 次 Alembic 迁移：

- `cases`
- `evidences`
- `case_timelines`
- `document_templates`
- `documents`
- `favorites`

---

## Sidebar Navigation Update

Phase 2 完成后侧边栏导航：

```
律智通
├── 仪表盘 (Dashboard)
├── 智能咨询 (Chat)
├── 案件管理 (Cases)          ← 新增
├── 文书中心 (Documents)       ← 新增
├── 合同审查 (Contracts)       ← 新增
├── 知识库 (Knowledge)
│   ├── 法规检索
│   └── 案例检索
├── 赔偿计算器 (Calculator)
├── 反馈看板 (Feedback)        ← 新增（管理员可见）
├── Token 监控
└── 设置 (Settings)
```

---

## Acceptance Criteria

- [ ] 案件完整 CRUD + 筛选搜索 + 状态流转
- [ ] 证据上传/分类/排序/预览
- [ ] 时间线事件管理
- [ ] 10 个文书模板可用，变量替换正确
- [ ] 文书富文本编辑器可用
- [ ] AI 文书生成内容合理（SSE流式）
- [ ] AI 案件分析输出结构化结果
- [ ] 合同上传 → OCR → 5维度审查 → 报告生成完整流程
- [ ] 知识库收藏 + 笔记功能
- [ ] AI 法规解读
- [ ] 用户评价组件集成到 Chat 页面
- [ ] 反馈聚合看板展示正确
- [ ] 侧边栏导航更新
- [ ] 免费版/专业版权限控制生效
