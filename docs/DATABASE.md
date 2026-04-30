# 律师AI助手 - 数据库设计文档

## 一、数据库概述

### 1.1 数据库选型

| 数据类型 | 数据库 | 说明 |
|----------|--------|------|
| 关系型数据 | PostgreSQL 15+ | 主数据库，存储业务数据 |
| 向量数据 | Milvus 2.x | 存储文本向量，用于语义检索 |
| 缓存 | Redis 7.x | 会话缓存、热点数据 |
| 文档存储 | MinIO / S3 | 文件存储（合同、证据等） |
| 搜索引擎 | Elasticsearch 8.x | 全文检索（可选） |

### 1.2 命名规范

| 规则 | 示例 |
|------|------|
| 表名 | 小写蛇形，复数：`users`, `cases`, `documents` |
| 字段名 | 小写蛇形：`created_at`, `case_number` |
| 主键 | `id`，BIGINT，自增或雪花算法 |
| 外键 | `{表名单数}_id`：`user_id`, `case_id` |
| 索引 | `idx_{表名}_{字段}`：`idx_cases_status` |
| 唯一索引 | `uk_{表名}_{字段}`：`uk_users_email` |

### 1.3 公共字段

所有业务表均包含以下公共字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| created_by | BIGINT | 创建人ID |
| updated_by | BIGINT | 更新人ID |
| is_deleted | BOOLEAN | 软删除标记 |

---

## 二、用户与权限模块

### 2.1 用户表 (users)

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,                    -- 租户ID（多租户）
    email VARCHAR(100) NOT NULL,                  -- 邮箱（登录账号）
    password_hash VARCHAR(255) NOT NULL,          -- 密码哈希
    salt VARCHAR(64) NOT NULL,                    -- 盐值
    name VARCHAR(50) NOT NULL,                    -- 姓名
    avatar_url VARCHAR(500),                      -- 头像URL
    phone VARCHAR(20),                            -- 手机号
    title VARCHAR(50),                            -- 职位（律师、合伙人等）
    license_number VARCHAR(50),                   -- 律师执业证号
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 状态：active/inactive/locked
    last_login_at TIMESTAMP,                      -- 最后登录时间
    last_login_ip VARCHAR(45),                    -- 最后登录IP
    settings JSONB,                               -- 用户设置（JSON）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT uk_users_email UNIQUE (tenant_id, email)
);

-- 索引
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_name ON users(name);

-- 注释
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.tenant_id IS '租户ID，用于多租户隔离';
COMMENT ON COLUMN users.license_number IS '律师执业证号';
COMMENT ON COLUMN users.settings IS '用户个人设置，如默认文书模板、通知偏好等';
```

### 2.2 角色表 (roles)

```sql
CREATE TABLE roles (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,                    -- 角色名称
    code VARCHAR(50) NOT NULL,                    -- 角色编码
    description VARCHAR(200),                     -- 角色描述
    is_system BOOLEAN NOT NULL DEFAULT FALSE,     -- 是否系统内置角色
    permissions JSONB NOT NULL,                   -- 权限列表（JSON数组）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT uk_roles_code UNIQUE (tenant_id, code)
);

-- 预置角色
-- admin: 系统管理员
-- managing_partner: 管理合伙人
-- partner: 合伙人
-- lawyer: 律师
-- assistant: 律师助理
-- intern: 实习生

COMMENT ON TABLE roles IS '角色表';
COMMENT ON COLUMN roles.permissions IS '权限列表，存储功能权限编码数组';
```

### 2.3 用户角色关联表 (user_roles)

```sql
CREATE TABLE user_roles (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,

    CONSTRAINT uk_user_roles UNIQUE (user_id, role_id),
    CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);

COMMENT ON TABLE user_roles IS '用户角色关联表';
```

### 2.4 租户表 (tenants)

```sql
CREATE TABLE tenants (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,                   -- 租户名称（律所名称）
    short_name VARCHAR(50),                       -- 简称
    logo_url VARCHAR(500),                        -- Logo URL
    address VARCHAR(200),                         -- 地址
    contact_name VARCHAR(50),                     -- 联系人
    contact_phone VARCHAR(20),                    -- 联系电话
    license_number VARCHAR(100),                  -- 律所执业证号
    plan VARCHAR(20) NOT NULL DEFAULT 'basic',    -- 套餐：basic/pro/enterprise
    max_users INT NOT NULL DEFAULT 10,            -- 最大用户数
    max_cases INT NOT NULL DEFAULT 100,           -- 最大案件数
    max_storage BIGINT NOT NULL DEFAULT 10737418240, -- 最大存储空间（字节）
    used_storage BIGINT NOT NULL DEFAULT 0,       -- 已用存储空间
    expire_at TIMESTAMP,                          -- 到期时间
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 状态
    settings JSONB,                               -- 租户设置
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE tenants IS '租户表（多租户）';
```

---

## 三、案件管理模块

### 3.1 案件表 (cases)

```sql
CREATE TABLE cases (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    case_number VARCHAR(100),                     -- 案号（法院/仲裁委编号）
    internal_number VARCHAR(100),                 -- 内部编号
    case_name VARCHAR(200) NOT NULL,              -- 案件名称
    case_type VARCHAR(50) NOT NULL,               -- 案件类型
    case_subtype VARCHAR(50),                     -- 案件子类型
    case_status VARCHAR(30) NOT NULL DEFAULT 'pending', -- 案件状态
    case_stage VARCHAR(30),                       -- 案件阶段：arbitration/first_appeal/second_appeal等
    court VARCHAR(100),                           -- 受理机构（法院/仲裁委）
    judge VARCHAR(50),                            -- 主审法官/仲裁员

    -- 委托人信息
    client_type VARCHAR(20) NOT NULL,             -- 委托人类型：employee/employer
    client_name VARCHAR(100) NOT NULL,            -- 委托人名称
    client_id_number VARCHAR(50),                 -- 委托人证件号
    client_phone VARCHAR(20),                     -- 委托人电话
    client_address VARCHAR(200),                  -- 委托人地址
    client_agent VARCHAR(50),                     -- 委托人代理人

    -- 对方当事人信息
    opposing_party_name VARCHAR(100),             -- 对方当事人名称
    opposing_party_id_number VARCHAR(50),         -- 对方证件号
    opposing_party_phone VARCHAR(20),             -- 对方电话
    opposing_party_address VARCHAR(200),          -- 对方地址
    opposing_party_agent VARCHAR(50),             -- 对方代理人

    -- 案件详情
    claim_amount DECIMAL(14,2),                   -- 标的金额
    claim_items JSONB,                            -- 诉讼请求列表
    dispute_focus TEXT[],                         -- 争议焦点
    case_summary TEXT,                            -- 案件摘要

    -- 办案信息
    lawyer_id BIGINT NOT NULL,                    -- 主办律师ID
    assistant_id BIGINT,                          -- 助理ID
    team_members BIGINT[],                        -- 团队成员ID数组

    -- 时间信息
    accepted_at DATE,                             -- 委托日期
    filed_at DATE,                                -- 立案日期
    closed_at DATE,                               -- 结案日期

    -- 结果信息
    case_result VARCHAR(30),                      -- 案件结果：win/lose/partial/settle
    result_amount DECIMAL(14,2),                  -- 获得金额
    result_summary TEXT,                          -- 结果摘要

    -- AI分析结果
    ai_analysis JSONB,                            -- AI分析结果（优势/风险/策略）
    win_probability DECIMAL(5,2),                 -- 胜诉概率（AI预测）

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_cases_lawyer FOREIGN KEY (lawyer_id) REFERENCES users(id),
    CONSTRAINT fk_cases_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- 索引
CREATE INDEX idx_cases_tenant ON cases(tenant_id);
CREATE INDEX idx_cases_lawyer ON cases(lawyer_id);
CREATE INDEX idx_cases_status ON cases(case_status);
CREATE INDEX idx_cases_type ON cases(case_type);
CREATE INDEX idx_cases_court ON cases(court);
CREATE INDEX idx_cases_client_name ON cases(client_name);
CREATE INDEX idx_cases_opposing_party ON cases(opposing_party_name);
CREATE INDEX idx_cases_accepted_at ON cases(accepted_at);
CREATE INDEX idx_cases_internal_number ON cases(internal_number);

-- 全文索引（案件名称、摘要）
CREATE INDEX idx_cases_fulltext ON cases USING GIN (
    to_tsvector('simple', case_name || ' ' || COALESCE(case_summary, ''))
);

COMMENT ON TABLE cases IS '案件表';
COMMENT ON COLUMN cases.case_type IS '案件类型：labor_contract/wage/injury/discrimination等';
COMMENT ON COLUMN cases.case_status IS '案件状态：pending/arbitration/first_appeal/second_appeal/closed/cancelled';
COMMENT ON COLUMN cases.claim_items IS '诉讼请求列表，JSON数组格式';
COMMENT ON COLUMN cases.ai_analysis IS 'AI分析结果，包含advantages、risks、strategies等字段';
```

### 3.2 案件时间线表 (case_timelines)

```sql
CREATE TABLE case_timelines (
    id BIGINT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    event_date DATE NOT NULL,                     -- 事件日期
    event_time TIME,                              -- 事件时间
    event_type VARCHAR(50) NOT NULL,              -- 事件类型
    event_title VARCHAR(200) NOT NULL,            -- 事件标题
    event_content TEXT,                           -- 事件内容
    is_key_event BOOLEAN NOT NULL DEFAULT FALSE,  -- 是否关键事件
    reminder_at TIMESTAMP,                        -- 提醒时间
    reminder_sent BOOLEAN NOT NULL DEFAULT FALSE, -- 是否已提醒
    attachments JSONB,                            -- 附件列表
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_timelines_case FOREIGN KEY (case_id) REFERENCES cases(id)
);

CREATE INDEX idx_timelines_case ON case_timelines(case_id);
CREATE INDEX idx_timelines_date ON case_timelines(event_date);
CREATE INDEX idx_timelines_type ON case_timelines(event_type);

COMMENT ON TABLE case_timelines IS '案件时间线表';
COMMENT ON COLUMN case_timelines.event_type IS '事件类型：accept/file/hearing/judgment/appeal/execute等';
```

### 3.3 证据表 (evidences)

```sql
CREATE TABLE evidences (
    id BIGINT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    evidence_number VARCHAR(50),                  -- 证据编号
    evidence_name VARCHAR(200) NOT NULL,          -- 证据名称
    evidence_type VARCHAR(50) NOT NULL,           -- 证据类型
    evidence_category VARCHAR(50),                -- 证据分类
    source VARCHAR(100),                          -- 证据来源
    obtain_date DATE,                             -- 获取日期
    page_count INT,                               -- 页数
    description TEXT,                             -- 证据说明
    prove_purpose TEXT,                           -- 证明目的
    is_original BOOLEAN NOT NULL DEFAULT TRUE,    -- 是否原件
    file_url VARCHAR(500),                        -- 文件URL
    file_name VARCHAR(200),                       -- 文件名
    file_size BIGINT,                             -- 文件大小
    file_type VARCHAR(50),                        -- 文件类型
    ocr_text TEXT,                                -- OCR识别文本
    ai_summary TEXT,                              -- AI摘要
    display_order INT NOT NULL DEFAULT 0,         -- 展示顺序
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_evidences_case FOREIGN KEY (case_id) REFERENCES cases(id)
);

CREATE INDEX idx_evidences_case ON evidences(case_id);
CREATE INDEX idx_evidences_type ON evidences(evidence_type);
CREATE INDEX idx_evidences_category ON evidences(evidence_category);

COMMENT ON TABLE evidences IS '证据表';
COMMENT ON COLUMN evidences.evidence_type IS '证据类型：contract/record/photo/video/audio/document等';
COMMENT ON COLUMN evidences.evidence_category IS '证据分类：本证/反证';
```

### 3.4 案件关联表 (case_relations)

```sql
CREATE TABLE case_relations (
    id BIGINT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    related_case_id BIGINT NOT NULL,              -- 关联案件ID
    relation_type VARCHAR(50) NOT NULL,           -- 关联类型
    description VARCHAR(200),                     -- 关联说明
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,

    CONSTRAINT uk_case_relations UNIQUE (case_id, related_case_id),
    CONSTRAINT fk_relations_case FOREIGN KEY (case_id) REFERENCES cases(id),
    CONSTRAINT fk_relations_related FOREIGN KEY (related_case_id) REFERENCES cases(id)
);

CREATE INDEX idx_relations_case ON case_relations(case_id);

COMMENT ON TABLE case_relations IS '案件关联表';
COMMENT ON COLUMN case_relations.relation_type IS '关联类型：appeal/retrial/related等';
```

---

## 四、文书管理模块

### 4.1 文书模板表 (document_templates)

```sql
CREATE TABLE document_templates (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT,                             -- 租户ID（NULL表示系统模板）
    name VARCHAR(100) NOT NULL,                   -- 模板名称
    code VARCHAR(50) NOT NULL,                    -- 模板编码
    category VARCHAR(50) NOT NULL,                -- 模板分类
    subcategory VARCHAR(50),                      -- 模牌子分类
    description VARCHAR(500),                     -- 模板描述
    content TEXT NOT NULL,                        -- 模板内容（支持变量占位符）
    variables JSONB,                              -- 变量定义
    format_rules JSONB,                           -- 格式规则
    is_system BOOLEAN NOT NULL DEFAULT FALSE,     -- 是否系统模板
    is_public BOOLEAN NOT NULL DEFAULT FALSE,     -- 是否公开模板
    use_count INT NOT NULL DEFAULT 0,             -- 使用次数
    rating DECIMAL(3,2),                          -- 评分
    tags VARCHAR(50)[],                           -- 标签
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_templates_tenant ON document_templates(tenant_id);
CREATE INDEX idx_templates_category ON document_templates(category);
CREATE INDEX idx_templates_code ON document_templates(code);

COMMENT ON TABLE document_templates IS '文书模板表';
COMMENT ON COLUMN document_templates.category IS '模板分类：application/indictment/defense/letter/agreement等';
COMMENT ON COLUMN document_templates.variables IS '变量定义，包含变量名、类型、默认值、是否必填等';
```

### 4.2 文书表 (documents)

```sql
CREATE TABLE documents (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    case_id BIGINT,                               -- 关联案件ID
    template_id BIGINT,                           -- 使用模板ID
    doc_number VARCHAR(100),                      -- 文书编号
    doc_type VARCHAR(50) NOT NULL,                -- 文书类型
    title VARCHAR(200) NOT NULL,                  -- 文书标题
    content TEXT NOT NULL,                        -- 文书内容
    html_content TEXT,                            -- HTML内容
    variables JSONB,                              -- 变量值
    ai_suggestions JSONB,                         -- AI建议
    status VARCHAR(30) NOT NULL DEFAULT 'draft',  -- 状态
    version INT NOT NULL DEFAULT 1,               -- 版本号
    word_count INT,                               -- 字数
    file_url VARCHAR(500),                        -- 导出文件URL
    file_name VARCHAR(200),                       -- 导出文件名
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_documents_case FOREIGN KEY (case_id) REFERENCES cases(id),
    CONSTRAINT fk_documents_template FOREIGN KEY (template_id) REFERENCES document_templates(id),
    CONSTRAINT fk_documents_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_documents_tenant ON documents(tenant_id);
CREATE INDEX idx_documents_case ON documents(case_id);
CREATE INDEX idx_documents_type ON documents(doc_type);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);

COMMENT ON TABLE documents IS '文书表';
COMMENT ON COLUMN documents.doc_type IS '文书类型：arbitration_application/indictment/defense/letter/agreement等';
COMMENT ON COLUMN documents.status IS '状态：draft/review/final/archived';
COMMENT ON COLUMN documents.ai_suggestions IS 'AI建议列表，包含建议类型、内容、位置等';
```

### 4.3 文书版本表 (document_versions)

```sql
CREATE TABLE document_versions (
    id BIGINT PRIMARY KEY,
    document_id BIGINT NOT NULL,
    version INT NOT NULL,
    content TEXT NOT NULL,
    html_content TEXT,
    change_summary VARCHAR(500),                  -- 变更摘要
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,

    CONSTRAINT uk_document_versions UNIQUE (document_id, version),
    CONSTRAINT fk_versions_document FOREIGN KEY (document_id) REFERENCES documents(id)
);

CREATE INDEX idx_versions_document ON document_versions(document_id);

COMMENT ON TABLE document_versions IS '文书版本表';
```

---

## 五、知识库模块

### 5.1 法规表 (laws)

```sql
CREATE TABLE laws (
    id BIGINT PRIMARY KEY,
    law_type VARCHAR(30) NOT NULL,                -- 法规类型
    name VARCHAR(200) NOT NULL,                   -- 法规名称
    short_name VARCHAR(100),                      -- 简称
    issuing_authority VARCHAR(100),               -- 发布机关
    document_number VARCHAR(100),                 -- 文号
    publish_date DATE,                            -- 发布日期
    effective_date DATE,                          -- 生效日期
    expiry_date DATE,                             -- 失效日期
    status VARCHAR(30) NOT NULL,                  -- 效力状态
    category VARCHAR(50),                         -- 分类
    tags VARCHAR(50)[],                           -- 标签
    content TEXT NOT NULL,                        -- 法规全文
    summary TEXT,                                 -- 摘要
    ai_interpretation TEXT,                       -- AI解读
    source_url VARCHAR(500),                      -- 来源URL
    view_count INT NOT NULL DEFAULT 0,            -- 浏览次数
    cite_count INT NOT NULL DEFAULT 0,            -- 引用次数
    embedding VECTOR(1536),                       -- 向量（用于语义检索）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 索引
CREATE INDEX idx_laws_type ON laws(law_type);
CREATE INDEX idx_laws_category ON laws(category);
CREATE INDEX idx_laws_status ON laws(status);
CREATE INDEX idx_laws_effective_date ON laws(effective_date);
CREATE INDEX idx_laws_name ON laws(name);

-- 全文索引
CREATE INDEX idx_laws_fulltext ON laws USING GIN (
    to_tsvector('simple', name || ' ' || COALESCE(content, ''))
);

COMMENT ON TABLE laws IS '法规表';
COMMENT ON COLUMN laws.law_type IS '法规类型：law/regulation/judicial_interpretation/local_reg等';
COMMENT ON COLUMN laws.status IS '效力状态：effective/expired/revised';
```

### 5.2 法条表 (law_articles)

```sql
CREATE TABLE law_articles (
    id BIGINT PRIMARY KEY,
    law_id BIGINT NOT NULL,
    article_number VARCHAR(50) NOT NULL,          -- 条号
    article_title VARCHAR(200),                   -- 条目标题
    content TEXT NOT NULL,                        -- 条文内容
    ai_interpretation TEXT,                       -- AI解读
    related_articles BIGINT[],                    -- 关联法条ID
    keywords VARCHAR(50)[],                       -- 关键词
    embedding VECTOR(1536),                       -- 向量
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_articles_law FOREIGN KEY (law_id) REFERENCES laws(id),
    CONSTRAINT uk_law_articles UNIQUE (law_id, article_number)
);

CREATE INDEX idx_articles_law ON law_articles(law_id);
CREATE INDEX idx_articles_number ON law_articles(article_number);

COMMENT ON TABLE law_articles IS '法条表';
```

### 5.3 案例表 (precedent_cases)

```sql
CREATE TABLE precedent_cases (
    id BIGINT PRIMARY KEY,
    case_number VARCHAR(100) NOT NULL,            -- 案号
    case_name VARCHAR(300),                       -- 案件名称
    court VARCHAR(100) NOT NULL,                  -- 法院
    court_level VARCHAR(30),                      -- 法院层级
    case_type VARCHAR(50) NOT NULL,               -- 案件类型
    procedure_type VARCHAR(30),                   -- 程序类型
    judge_date DATE,                              -- 裁判日期
    publish_date DATE,                            -- 发布日期

    -- 当事人信息
    plaintiff VARCHAR(200),                       -- 原告
    defendant VARCHAR(200),                       -- 被告
    plaintiff_agent VARCHAR(200),                 -- 原告代理人
    defendant_agent VARCHAR(200),                 -- 被告代理人

    -- 案件内容
    claim TEXT,                                   -- 诉讼请求
    fact_found TEXT,                              -- 查明事实
    court_opinion TEXT,                           -- 本院认为
    judgment TEXT,                                -- 裁判结果
    full_text TEXT,                               -- 裁判文书全文

    -- 结构化信息
    dispute_focus TEXT[],                         -- 争议焦点
    legal_basis JSONB,                            -- 法律依据
    judgment_result VARCHAR(30),                  -- 裁判结果类型
    claim_supported DECIMAL(5,2),                 -- 诉请支持比例

    -- AI处理
    summary TEXT,                                 -- AI摘要
    key_points JSONB,                             -- 关键要点
    ai_analysis JSONB,                            -- AI分析

    -- 统计信息
    view_count INT NOT NULL DEFAULT 0,
    cite_count INT NOT NULL DEFAULT 0,

    -- 向量
    embedding VECTOR(1536),

    source_url VARCHAR(500),                      -- 来源URL
    source VARCHAR(50),                           -- 数据来源
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT uk_precedent_cases UNIQUE (case_number)
);

-- 索引
CREATE INDEX idx_precedent_court ON precedent_cases(court);
CREATE INDEX idx_precedent_court_level ON precedent_cases(court_level);
CREATE INDEX idx_precedent_case_type ON precedent_cases(case_type);
CREATE INDEX idx_precedent_procedure ON precedent_cases(procedure_type);
CREATE INDEX idx_precedent_judge_date ON precedent_cases(judge_date);
CREATE INDEX idx_precedent_result ON precedent_cases(judgment_result);

-- 全文索引
CREATE INDEX idx_precedent_fulltext ON precedent_cases USING GIN (
    to_tsvector('simple',
        COALESCE(case_name, '') || ' ' ||
        COALESCE(full_text, '') || ' ' ||
        COALESCE(dispute_focus::text, '')
    )
);

COMMENT ON TABLE precedent_cases IS '案例表';
COMMENT ON COLUMN precedent_cases.court_level IS '法院层级：supreme/higher/intermediate/grassroot';
COMMENT ON COLUMN precedent_cases.procedure_type IS '程序类型：first_appeal/second_appeal/retrial';
COMMENT ON COLUMN precedent_cases.judgment_result IS '裁判结果：plaintiff_win/defendant_win/partial/settle';
```

### 5.4 知识收藏表 (knowledge_favorites)

```sql
CREATE TABLE knowledge_favorites (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    target_type VARCHAR(30) NOT NULL,             -- 收藏类型
    target_id BIGINT NOT NULL,                    -- 收藏目标ID
    folder VARCHAR(100),                          -- 收藏夹
    notes TEXT,                                   -- 笔记
    tags VARCHAR(50)[],                           -- 标签
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_knowledge_favorites UNIQUE (user_id, target_type, target_id),
    CONSTRAINT fk_favorites_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_favorites_user ON knowledge_favorites(user_id);
CREATE INDEX idx_favorites_target ON knowledge_favorites(target_type, target_id);

COMMENT ON TABLE knowledge_favorites IS '知识收藏表';
COMMENT ON COLUMN knowledge_favorites.target_type IS '收藏类型：law/article/case/document';
```

---

## 六、AI对话模块

### 6.1 对话会话表 (chat_sessions)

```sql
CREATE TABLE chat_sessions (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    case_id BIGINT,                               -- 关联案件ID
    title VARCHAR(200),                           -- 会话标题
    summary TEXT,                                 -- 会话摘要
    message_count INT NOT NULL DEFAULT 0,         -- 消息数量
    tokens_used INT NOT NULL DEFAULT 0,           -- 消耗token数
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 状态
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_sessions_case FOREIGN KEY (case_id) REFERENCES cases(id)
);

CREATE INDEX idx_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_sessions_case ON chat_sessions(case_id);
CREATE INDEX idx_sessions_created_at ON chat_sessions(created_at);

COMMENT ON TABLE chat_sessions IS '对话会话表';
```

### 6.2 对话消息表 (chat_messages)

```sql
CREATE TABLE chat_messages (
    id BIGINT PRIMARY KEY,
    session_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,                    -- 角色：user/assistant/system
    content TEXT NOT NULL,                        -- 消息内容
    content_type VARCHAR(30) DEFAULT 'text',      -- 内容类型
    attachments JSONB,                            -- 附件列表
    legal_basis JSONB,                            -- 引用法条
    cases_referenced BIGINT[],                    -- 引用案例ID
    feedback VARCHAR(20),                         -- 用户反馈
    feedback_content TEXT,                        -- 反馈内容
    tokens INT,                                   -- token数量
    model VARCHAR(50),                            -- 使用模型
    latency INT,                                  -- 响应耗时（毫秒）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_messages_session FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

CREATE INDEX idx_messages_session ON chat_messages(session_id);
CREATE INDEX idx_messages_role ON chat_messages(role);
CREATE INDEX idx_messages_created_at ON chat_messages(created_at);

COMMENT ON TABLE chat_messages IS '对话消息表';
COMMENT ON COLUMN chat_messages.content_type IS '内容类型：text/markdown/json';
COMMENT ON COLUMN chat_messages.feedback IS '用户反馈：helpful/not_helpful';
```

---

## 七、计算器模块

### 7.1 计算记录表 (calculation_records)

```sql
CREATE TABLE calculation_records (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    case_id BIGINT,                               -- 关联案件ID
    calculation_type VARCHAR(50) NOT NULL,        -- 计算类型
    input_params JSONB NOT NULL,                  -- 输入参数
    output_result JSONB NOT NULL,                 -- 输出结果
    basis TEXT,                                   -- 计算依据
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_calc_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_calc_case FOREIGN KEY (case_id) REFERENCES cases(id)
);

CREATE INDEX idx_calc_user ON calculation_records(user_id);
CREATE INDEX idx_calc_type ON calculation_records(calculation_type);
CREATE INDEX idx_calc_case ON calculation_records(case_id);

COMMENT ON TABLE calculation_records IS '计算记录表';
COMMENT ON COLUMN calculation_records.calculation_type IS '计算类型：illegal_termination/overtime/injury/annual_leave等';
```

---

## 八、系统配置模块

### 8.1 系统配置表 (system_configs)

```sql
CREATE TABLE system_configs (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT,                             -- 租户ID（NULL表示全局配置）
    config_key VARCHAR(100) NOT NULL,             -- 配置键
    config_value TEXT NOT NULL,                   -- 配置值
    config_type VARCHAR(30) NOT NULL,             -- 配置类型
    description VARCHAR(200),                     -- 配置说明
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_system_configs UNIQUE (tenant_id, config_key)
);

CREATE INDEX idx_configs_tenant ON system_configs(tenant_id);
CREATE INDEX idx_configs_key ON system_configs(config_key);

COMMENT ON TABLE system_configs IS '系统配置表';
```

### 8.2 操作日志表 (operation_logs)

```sql
CREATE TABLE operation_logs (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT,
    user_id BIGINT,
    module VARCHAR(50) NOT NULL,                  -- 模块
    action VARCHAR(50) NOT NULL,                  -- 操作
    target_type VARCHAR(50),                      -- 目标类型
    target_id BIGINT,                             -- 目标ID
    content JSONB,                                -- 操作内容
    ip_address VARCHAR(45),                       -- IP地址
    user_agent VARCHAR(500),                      -- 用户代理
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 创建分区（按月）
CREATE TABLE operation_logs_202401 PARTITION OF operation_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE operation_logs_202402 PARTITION OF operation_logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- ... 后续月份分区

CREATE INDEX idx_logs_user ON operation_logs(user_id);
CREATE INDEX idx_logs_module ON operation_logs(module);
CREATE INDEX idx_logs_created_at ON operation_logs(created_at);

COMMENT ON TABLE operation_logs IS '操作日志表（按月分区）';
```

### 8.3 通知表 (notifications)

```sql
CREATE TABLE notifications (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    type VARCHAR(50) NOT NULL,                    -- 通知类型
    title VARCHAR(200) NOT NULL,                  -- 标题
    content TEXT NOT NULL,                        -- 内容
    target_type VARCHAR(50),                      -- 目标类型
    target_id BIGINT,                             -- 目标ID
    is_read BOOLEAN NOT NULL DEFAULT FALSE,       -- 是否已读
    read_at TIMESTAMP,                            -- 阅读时间
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

COMMENT ON TABLE notifications IS '通知表';
```

---

## 九、向量数据库设计（Milvus）

### 9.1 法条向量集合

```python
# 法条向量集合
collection_name = "law_articles_vectors"

# 字段定义
fields = [
    {"name": "id", "dtype": "INT64", "is_primary": True, "auto_id": False},
    {"name": "law_id", "dtype": "INT64"},           # 法规ID
    {"name": "article_number", "dtype": "VARCHAR", "max_length": 50},  # 条号
    {"name": "content", "dtype": "VARCHAR", "max_length": 2000},  # 条文内容
    {"name": "embedding", "dtype": "FLOAT_VECTOR", "dim": 1536},   # 向量
]

# 索引
index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}
```

### 9.2 案例向量集合

```python
# 案例向量集合
collection_name = "precedent_cases_vectors"

# 字段定义
fields = [
    {"name": "id", "dtype": "INT64", "is_primary": True, "auto_id": False},
    {"name": "case_id", "dtype": "INT64"},          # 案例ID
    {"name": "case_number", "dtype": "VARCHAR", "max_length": 100},  # 案号
    {"name": "case_type", "dtype": "VARCHAR", "max_length": 50},     # 案件类型
    {"name": "summary", "dtype": "VARCHAR", "max_length": 2000},     # 摘要
    {"name": "embedding", "dtype": "FLOAT_VECTOR", "dim": 1536},     # 向量
]
```

---

## 十、Redis缓存设计

### 10.1 缓存键设计

| 缓存键 | 类型 | TTL | 说明 |
|--------|------|-----|------|
| `user:{user_id}` | Hash | 24h | 用户信息缓存 |
| `session:{session_id}` | Hash | 30m | 会话信息缓存 |
| `law:{law_id}` | Hash | 7d | 法规详情缓存 |
| `article:{article_id}` | Hash | 7d | 法条详情缓存 |
| `template:{template_id}` | Hash | 24h | 模板缓存 |
| `chat:history:{session_id}` | List | 7d | 对话历史缓存 |
| `search:result:{hash}` | Hash | 1h | 搜索结果缓存 |
| `rate:limit:{user_id}:{action}` | String | 1m | 限流计数器 |

### 10.2 缓存策略

```yaml
# 缓存策略
user_info:
  key: "user:{user_id}"
  ttl: 86400  # 24小时
  strategy: cache_aside

law_detail:
  key: "law:{law_id}"
  ttl: 604800  # 7天
  strategy: cache_aside
  invalidation: on_update

chat_history:
  key: "chat:history:{session_id}"
  ttl: 604800  # 7天
  max_length: 100
  strategy: write_through
```

---

## 十一、数据字典

### 11.1 案件状态 (case_status)

| 编码 | 名称 | 说明 |
|------|------|------|
| pending | 待立案 | 案件创建，尚未立案 |
| arbitration | 仲裁中 | 仲裁阶段 |
| first_appeal | 一审中 | 一审阶段 |
| second_appeal | 二审中 | 二审阶段 |
| retrial | 再审中 | 再审阶段 |
| execution | 执行中 | 执行阶段 |
| closed | 已结案 | 案件已结 |
| cancelled | 已撤销 | 案件已撤销 |

### 11.2 案件类型 (case_type)

| 编码 | 名称 | 说明 |
|------|------|------|
| labor_contract | 劳动合同纠纷 | |
| wage | 劳动报酬纠纷 | |
| injury | 工伤保险纠纷 | |
| social_insurance | 社会保险纠纷 | |
| termination | 解除劳动关系纠纷 | |
| discrimination | 就业歧视纠纷 | |
| other | 其他劳动纠纷 | |

### 11.3 文书状态 (document_status)

| 编码 | 名称 | 说明 |
|------|------|------|
| draft | 草稿 | |
| review | 审核中 | |
| final | 定稿 | |
| archived | 已归档 | |

### 11.4 证据类型 (evidence_type)

| 编码 | 名称 | 说明 |
|------|------|------|
| contract | 合同 | |
| record | 记录 | 考勤记录、工资条等 |
| photo | 照片 | |
| video | 视频 | |
| audio | 音频 | 录音 |
| document | 文书 | 通知、决定书等 |
| communication | 通讯记录 | 聊天记录、邮件等 |
| witness | 证人证言 | |
| other | 其他 | |

---

## 十二、ER图

```
┌─────────────┐       ┌─────────────┐
│   tenants   │       │    users    │
├─────────────┤       ├─────────────┤
│ id          │◄──────│ tenant_id   │
│ name        │       │ id          │
│ plan        │       │ email       │
│ ...         │       │ name        │
└─────────────┘       │ role_id     │
      │               └─────────────┘
      │                     │
      │     ┌───────────────┼───────────────┐
      │     │               │               │
      ▼     ▼               ▼               ▼
┌─────────────┐       ┌─────────────┐ ┌─────────────┐
│   cases     │       │  documents  │ │chat_sessions│
├─────────────┤       ├─────────────┤ ├─────────────┤
│ id          │       │ id          │ │ id          │
│ tenant_id   │       │ tenant_id   │ │ user_id     │
│ lawyer_id   │───────│ case_id     │ │ case_id     │
│ case_name   │       │ title       │ │ title       │
│ ...         │       │ content     │ │ ...         │
└─────────────┘       └─────────────┘ └─────────────┘
      │                     │               │
      │                     │               │
      ▼                     ▼               ▼
┌─────────────┐       ┌─────────────┐ ┌─────────────┐
│case_timelines│      │doc_versions │ │chat_messages│
├─────────────┤       ├─────────────┤ ├─────────────┤
│ case_id     │       │ document_id │ │ session_id  │
│ event_date  │       │ version     │ │ role        │
│ ...         │       │ content     │ │ content     │
└─────────────┘       └─────────────┘ └─────────────┘
      │
      ▼
┌─────────────┐
│  evidences  │
├─────────────┤
│ case_id     │
│ evidence_   │
│ name        │
│ ...         │
└─────────────┘
```

---

## 十三、性能优化建议

### 13.1 索引优化

1. **高频查询字段建立复合索引**
   ```sql
   -- 案件列表查询
   CREATE INDEX idx_cases_list ON cases(tenant_id, case_status, created_at DESC);

   -- 文书列表查询
   CREATE INDEX idx_documents_list ON documents(tenant_id, case_id, created_at DESC);
   ```

2. **大表分区**
   - `operation_logs` 按月分区
   - `chat_messages` 按月分区

3. **全文索引**
   - 法规内容、案例内容建立全文索引
   - 使用PostgreSQL的`to_tsvector`

### 13.2 查询优化

1. **使用EXPLAIN分析慢查询**
2. **避免SELECT ***，只查询需要的字段
3. **合理使用JOIN，避免子查询**
4. **使用分页查询，避免一次性加载大量数据**

### 13.3 缓存策略

1. **热点数据缓存**：法规详情、模板
2. **会话数据缓存**：用户信息、权限
3. **搜索结果缓存**：相同查询条件

---

## 十四、数据安全

### 14.1 数据加密

| 数据类型 | 加密方式 | 说明 |
|----------|----------|------|
| 密码 | bcrypt | 单向哈希 |
| 证件号 | AES-256 | 可逆加密 |
| 手机号 | AES-256 | 可逆加密 |
| 文件 | AES-256 | 存储加密 |

### 14.2 数据隔离

1. **多租户隔离**：所有业务表包含`tenant_id`
2. **行级安全策略**：PostgreSQL RLS
3. **视图隔离**：按租户创建视图

### 14.3 数据备份

| 备份类型 | 频率 | 保留时间 |
|----------|------|----------|
| 全量备份 | 每日 | 30天 |
| 增量备份 | 每小时 | 7天 |
| 日志备份 | 每15分钟 | 3天 |

---

**文档版本**: V1.0
**创建日期**: 2024年1月
**维护团队**: 技术团队
