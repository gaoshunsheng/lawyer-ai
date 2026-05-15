# Phase 3 高级功能设计文档

> 版本: 1.0 | 日期: 2026-05-15 | 阶段: Phase 3 高级功能 (第13-18周)

## 概述

Phase 3 在 Phase 1 (基础架构) 和 Phase 2 (核心工作流) 的基础上，添加5个高级功能模块，形成差异化竞争力。本文档定义每个模块的数据模型、API接口、前端页面、AI Agent架构和文件结构。

### 技术栈新增

| 组件 | 版本 | 用途 |
|------|------|------|
| recharts | ^2.12 | 数据报表图表 |
| openpyxl | ^3.1 | Excel导出 |
| reportlab | ^4.2 | PDF导出 |
| python-docx | ^1.1 | Word导出 |
| PyPDF2 | ^3.0 | PDF解析 |

---

## 模块一：AI庭审模拟 (Weeks 13-14)

### 1.1 功能说明

AI扮演对方律师/法官角色，模拟庭审辩论，帮助律师预演争议焦点、检验论据强度。支持4种模拟模式和3种角色视角。

### 1.2 数据模型

#### trial_simulations 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| case_id | UUID | FK cases.id | 关联案件 |
| tenant_id | UUID | FK tenants.id | 租户 |
| user_id | UUID | FK users.id | 发起用户 |
| mode | VARCHAR(20) | NOT NULL | 模拟模式: arbitration/first_instance/defense/judgment |
| role | VARCHAR(20) | NOT NULL | 用户角色: plaintiff/defendant/judge |
| status | VARCHAR(20) | DEFAULT 'active' | 状态: active/completed/abandoned |
| rounds_completed | INTEGER | DEFAULT 0 | 已完成轮数 |
| dispute_focus | JSONB | | AI生成的争议焦点列表 |
| strategy_report | JSONB | | 最终策略报告 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMPTZ | DEFAULT now() | 更新时间 |

#### trial_rounds 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| simulation_id | UUID | FK trial_simulations.id | 关联模拟 |
| round_num | INTEGER | NOT NULL | 轮次序号 |
| role | VARCHAR(20) | NOT NULL | 发言角色: ai/user |
| content | TEXT | NOT NULL | 发言内容 |
| argument_strength | VARCHAR(10) | | 论据强度: strong/medium/weak (仅user轮次) |
| evaluation | JSONB | | AI评估结果 (仅user轮次) |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |

### 1.3 API 接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/v1/cases/{case_id}/trial/start | 发起庭审模拟 | 登录用户 |
| POST | /api/v1/trial/{sim_id}/respond (SSE) | 律师回应，AI反驳(流式) | 登录用户 |
| POST | /api/v1/trial/{sim_id}/end | 结束模拟，生成策略报告 | 登录用户 |
| GET | /api/v1/trial/{sim_id} | 获取模拟详情 | 登录用户 |
| GET | /api/v1/trial/{sim_id}/rounds | 获取所有轮次记录 | 登录用户 |
| GET | /api/v1/trial/{sim_id}/report | 获取策略报告 | 登录用户 |
| GET | /api/v1/cases/{case_id}/trials | 获取案件的模拟历史 | 登录用户 |

### 1.4 AI Agent 架构

#### LangGraph StateGraph — 7节点

```
init_simulation → ai_attack → check_end → user_respond → evaluate_arg → ai_counter ─┐
                       ↑                                                               │
                       └───────────────────────────────────────────────────────────────┘
                                                                               
(用户调用end时) → generate_strategy_report → END
```

**TrialState TypedDict:**
```python
class TrialState(TypedDict):
    case_data: dict
    simulation_id: str
    mode: str          # arbitration/first_instance/defense/judgment
    user_role: str     # plaintiff/defendant/judge
    dispute_focus: list[str]
    current_round: int
    ai_message: str
    user_message: str
    argument_strength: str
    evaluation: dict
    strategy_report: dict
    error: str
```

**节点说明:**
- `init_simulation`: 加载案件材料，AI生成争议焦点Top 5
- `ai_attack`: AI根据角色提出质疑/反驳 (GLM-5.1, SSE流式)
- `check_end`: 检查是否用户请求结束
- `user_respond`: 等待律师输入(实际由API调用驱动，非graph内部等待)
- `evaluate_arg`: 评估用户论据强度 (GLM-5-Turbo, JSON输出)
- `ai_counter`: AI追问/转换攻击角度 (GLM-5.1)
- `generate_strategy_report`: 生成最终策略报告 (GLM-5.1, JSON输出)

**实际执行模式:** 不是单一ainvoke，而是分步调用:
1. `start`: 调用init + ai_attack，返回首轮AI发言
2. `respond`: 调用evaluate + ai_counter，返回评估+下一轮AI发言
3. `end`: 调用generate_strategy_report

### 1.5 文件结构

```
backend/app/
  ai/graphs/trial_graph.py          # 7节点StateGraph
  ai/prompts/trial_prompts.py       # 6个prompt (init/attack/evaluate/counter/report/followup)
  models/trial.py                   # TrialSimulation, TrialRound
  schemas/trial.py                  # TrialStartRequest, RoundResponse, StrategyReport
  services/trial_service.py         # CRUD + round management
  api/v1/trial.py                   # 7个API端点

frontend/src/
  app/(dashboard)/trial/page.tsx                  # 模拟列表页
  app/(dashboard)/trial/[id]/page.tsx             # 模拟界面(角色选择+辩论+报告)
  types/index.ts                                  # TrialSimulation, TrialRound类型
  lib/constants.ts                                # TRIAL_MODES, TRIAL_ROLES
```

---

## 模块二：甘特图项目管理 (Weeks 14-15)

### 2.1 功能说明

案件进度可视化管理，使用CSS-based甘特图支持拖拽编辑、任务分配、超期预警。基于案件类型自动生成标准流程节点。

### 2.2 数据模型

**使用现有 `cases.gantt_data` JSONB 字段**，无需新表。

#### gantt_data 结构

```json
{
  "nodes": [
    {
      "id": "node-1",
      "title": "仲裁申请",
      "type": "milestone",       // deadline/milestone/task/ai_assisted
      "start": "2026-05-15",
      "end": "2026-05-20",
      "assignee_id": "uuid-or-null",
      "status": "pending",       // pending/in_progress/completed/overdue
      "progress": 0,             // 0-100
      "description": "向劳动仲裁委员会提交申请"
    }
  ],
  "dependencies": [
    {"from": "node-1", "to": "node-2", "type": "finish_to_start"}
  ]
}
```

#### 节点类型配色

| 类型 | 颜色 | 说明 |
|------|------|------|
| deadline | red (#ef4444) | 法定期限 |
| milestone | blue (#3b82f6) | 关键里程碑 |
| task | green (#22c55e) | 任务节点 |
| ai_assisted | purple (#a855f7) | AI辅助节点 |

### 2.3 预设模板

| 案件类型 | 节点数 | 关键路径 |
|----------|--------|----------|
| labor_arbitration | 8 | 咨询→立案→举证→答辩→开庭→裁决→执行 |
| first_instance | 10 | 起诉→立案→举证→答辩→开庭→判决 |
| second_instance | 7 | 上诉→立案→阅卷→开庭→判决 |
| non_litigation | 5 | 咨询→调查→方案→谈判→协议 |

### 2.4 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/cases/{case_id}/gantt | 获取甘特图数据 |
| PUT | /api/v1/cases/{case_id}/gantt | 更新甘特图数据(全量替换) |
| POST | /api/v1/cases/{case_id}/gantt/apply-template | 按案件类型应用模板 |

### 2.5 超期预警逻辑

- `end < today` 且 `status != completed` → 标红 (overdue)
- `end - today <= 3天` 且 `status != completed` → 标黄 (warning)
- 前端计算，不存储预警状态

### 2.6 文件结构

```
backend/app/
  services/gantt_service.py         # gantt_data CRUD + 模板生成
  schemas/gantt.py                  # GanttNode, GanttDependency, GanttData
  api/v1/gantt.py                   # 3个API端点

frontend/src/
  app/(dashboard)/cases/[id]/gantt/page.tsx    # 甘特图页面
  components/gantt/gantt-chart.tsx             # 甘特图组件(CSS-based)
  components/gantt/gantt-node.tsx              # 单个节点组件
  components/gantt/gantt-toolbar.tsx           # 工具栏(缩放/视图切换)
```

---

## 模块三：数据报表/BI (Weeks 15-16)

### 3.1 功能说明

基于案件数据的多维度分析报表，使用Recharts渲染图表。支持案件概览、趋势分析、律师绩效、客户报告和数据导出。

### 3.2 数据模型

**无需新表**，全部从现有表聚合:
- `cases` → 案件数量、类型分布、状态分布、金额统计、胜诉率、周期
- `users` → 律师绩效排名
- `response_feedback` → 客户满意度
- `chat_sessions` + `chat_messages` → 咨询量统计

### 3.3 API 接口

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | /api/v1/reports/case-overview | 案件概览 | start_date, end_date |
| GET | /api/v1/reports/trends | 趋势分析 | granularity (month/quarter/year) |
| GET | /api/v1/reports/lawyer-performance | 律师绩效 | period (30/90/365 days) |
| GET | /api/v1/reports/client-report | 客户报告 | client_name, start_date, end_date |
| GET | /api/v1/reports/export | 数据导出 | format (xlsx/pdf), report_type |

### 3.4 报表类型与图表

#### 案件概览 (case-overview)

```json
{
  "total": 120,
  "by_type": [{"type": "labor_contract", "count": 45, "amount": 2300000}],
  "by_status": [{"status": "active", "count": 30}, ...],
  "avg_duration_days": 45,
  "win_rate": 0.72,
  "total_claim_amount": 8500000
}
```

图表: Recharts PieChart (类型分布) + BarChart (状态分布)

#### 趋势分析 (trends)

```json
{
  "periods": [
    {"period": "2026-01", "total": 12, "by_type": {"labor_contract": 5, ...}, "avg_amount": 50000}
  ]
}
```

图表: Recharts LineChart (案件量) + StackedBarChart (类型趋势)

#### 律师绩效 (lawyer-performance)

```json
{
  "lawyers": [
    {
      "user_id": "uuid", "name": "张律师",
      "total_cases": 25, "win_rate": 0.85, "avg_satisfaction": 4.5,
      "total_claim_amount": 1500000, "avg_duration_days": 38
    }
  ],
  "period_days": 90
}
```

图表: 排名表 + 进度条

#### 客户报告 (client-report)

```json
{
  "client_name": "某公司",
  "summary": {"total_cases": 5, "active": 2, "total_amount": 500000},
  "cases": [...],
  "timeline": [...]
}
```

图表: 汇总卡片 + 时间线

### 3.5 文件结构

```
backend/app/
  services/report_service.py        # 聚合查询
  schemas/report.py                 # 各报表Response schema
  api/v1/reports.py                 # 5个API端点

frontend/src/
  app/(dashboard)/reports/page.tsx                      # 报表主页(概览+趋势)
  app/(dashboard)/reports/lawyer-performance/page.tsx   # 律师绩效页
  app/(dashboard)/reports/client/page.tsx               # 客户报告页
  components/reports/case-overview-chart.tsx            # 概览图表
  components/reports/trend-chart.tsx                    # 趋势图表
  components/reports/lawyer-ranking-table.tsx           # 律师排名表
```

---

## 模块四：咨询增强 (Weeks 16-17)

### 4.1 功能说明

在现有智能咨询基础上增加: 追问引导(最多3轮)、文件附件上传解析、对话导出Word/PDF、对话关联案件。

### 4.2 数据模型变更

#### chat_sessions 表新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| case_id | UUID FK cases.id NULL | 关联案件ID |
| follow_up_count | INTEGER DEFAULT 0 | 当前追问轮数 |

#### chat_messages 表新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| attachments | JSONB | 附件列表 [{filename, url, type, size}] |
| is_follow_up | BOOLEAN DEFAULT FALSE | 是否为追问 |

### 4.3 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/chat/sessions/{id}/attachments | 上传附件 |
| POST | /api/v1/chat/sessions/{id}/link-case | 关联案件 |
| POST | /api/v1/chat/sessions/{id}/export | 导出对话(Word/PDF) |
| DELETE | /api/v1/chat/sessions/{id}/link-case | 取消关联 |

### 4.4 追问引导逻辑

在 `consult_graph.py` 中修改 `generate_answer` 节点:
1. AI生成回答后，检查是否有缺失的关键信息(当事人、金额、时间等)
2. 如有缺失且 follow_up_count < 3，生成追问问题
3. 返回追问标记 `follow_up: {question, missing_info}`

### 4.5 文件附件解析流程

```
上传文件 → 保存到Supabase Storage → 解析内容:
  - PDF: PyPDF2 提取文本
  - Word: python-docx 提取段落
  - 图片: 跳过OCR(未来增强)
→ 将文本内容注入对话上下文 → AI回答
```

### 4.6 文件结构

```
backend/app/
  services/chat_service.py          # 增加 export_attachment + link_case
  services/file_parser.py           # 新文件: PDF/Word解析
  api/v1/chat.py                    # 增加3个端点
  ai/graphs/consult_graph.py        # 修改: 增加追问逻辑
  ai/prompts/legal_prompts.py       # 增加 FOLLOW_UP_PROMPT

frontend/src/
  app/(dashboard)/chat/page.tsx     # 增强: 文件上传按钮、案件关联选择器
```

---

## 模块五：文书增强 (Weeks 17-18)

### 5.1 功能说明

在现有文书中心基础上增强: 版本对比/回退、法条/案例一键插入、计算器集成、批量文书生成。

### 5.2 数据模型

**无需新表。** 使用现有 Document 模型的 `parent_id` 自引用关系进行版本管理。

### 5.3 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/documents/{id}/versions | 获取版本历史列表 |
| GET | /api/v1/documents/{id}/versions/{v2}/diff | 对比两个版本 |
| POST | /api/v1/documents/{id}/versions/{vid}/rollback | 回退到指定版本 |
| POST | /api/v1/documents/search-in-context | 根据文书内容搜索法条/案例 |
| POST | /api/v1/documents/{id}/embed-calculation | 在文书中嵌入计算结果 |
| POST | /api/v1/documents/batch-generate | 批量生成文书 |

### 5.4 版本对比

使用 Python `difflib.unified_diff` 生成差异，返回结构化结果:
```json
{
  "old_version": 1,
  "new_version": 2,
  "diffs": [
    {"type": "added", "line": 5, "content": "新增条款内容"},
    {"type": "removed", "line": 3, "content": "删除的旧内容"}
  ]
}
```

### 5.5 法条/案例一键插入

在编辑器内提供搜索弹窗:
1. 根据文书当前内容和光标位置推断需要的法条/案例类型
2. 调用 `/search-in-context` 获取结果列表
3. 用户选择后，插入格式化引用文本

### 5.6 文件结构

```
backend/app/
  services/document_service.py      # 增加 version_diff, rollback, batch_generate
  api/v1/documents.py               # 增加6个端点

frontend/src/
  app/(dashboard)/documents/[id]/page.tsx      # 增强: 版本历史面板、搜索插入弹窗
  components/document/version-panel.tsx        # 版本历史面板
  components/document/law-insert-dialog.tsx   # 法条搜索插入弹窗
```

---

## 全局变更

### 前端导航新增

```typescript
// layout.tsx navItems 新增:
{ href: "/trial", label: "庭审模拟", icon: "⚖️" },
{ href: "/reports", label: "数据报表", icon: "📊" },
```

### 数据库迁移

| 迁移文件 | 内容 |
|----------|------|
| add_trial_tables.py | trial_simulations + trial_rounds |
| add_chat_session_fields.py | chat_sessions 增加 case_id, follow_up_count |
| add_chat_message_fields.py | chat_messages 增加 attachments, is_follow_up |

### 后端依赖

```
# requirements.txt 新增:
recharts 前端依赖 (npm install recharts)
openpyxl>=3.1.0
reportlab>=4.2.0
python-docx>=1.1.0
PyPDF2>=3.0.0
```

---

## 验收标准

- [ ] 庭审模拟可进行多轮辩论，生成策略报告
- [ ] 甘特图可视化+拖拽正常，支持4种节点类型
- [ ] 数据报表4种图表展示正确 (PieChart, BarChart, LineChart, 排名表)
- [ ] 咨询追问最多3轮，文件上传解析正常
- [ ] 文书版本对比/回退正常，法条一键插入可用
- [ ] 所有现有198个测试继续通过
- [ ] 新增测试 150+ 个
