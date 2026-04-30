-- 律师AI助手数据库初始化脚本
-- PostgreSQL

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 租户表（律所）
-- ==========================================
CREATE TABLE IF NOT EXISTS tenants (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '律所名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '律所编码',
    contact_person VARCHAR(50) COMMENT '联系人',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    address VARCHAR(200) COMMENT '地址',
    status INTEGER DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    expire_time TIMESTAMP COMMENT '到期时间',
    max_users INTEGER DEFAULT 10 COMMENT '最大用户数',
    current_user_count INTEGER DEFAULT 0 COMMENT '当前用户数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted INTEGER DEFAULT 0
);

COMMENT ON TABLE tenants IS '租户表（律所）';
COMMENT ON COLUMN tenants.id IS '主键ID';
COMMENT ON COLUMN tenants.name IS '律所名称';
COMMENT ON COLUMN tenants.code IS '律所编码';
COMMENT ON COLUMN tenants.contact_person IS '联系人';
COMMENT ON COLUMN tenants.contact_phone IS '联系电话';
COMMENT ON COLUMN tenants.address IS '地址';
COMMENT ON COLUMN tenants.status IS '状态：0-禁用，1-启用';
COMMENT ON COLUMN tenants.expire_time IS '到期时间';
COMMENT ON COLUMN tenants.max_users IS '最大用户数';
COMMENT ON COLUMN tenants.current_user_count IS '当前用户数';

-- ==========================================
-- 用户表
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    real_name VARCHAR(50) COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    role VARCHAR(20) NOT NULL COMMENT '角色',
    tenant_id BIGINT COMMENT '租户ID',
    avatar VARCHAR(200) COMMENT '头像URL',
    status INTEGER DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    last_login_time TIMESTAMP COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) COMMENT '最后登录IP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted INTEGER DEFAULT 0,
    CONSTRAINT fk_user_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '主键ID';
COMMENT ON COLUMN users.username IS '用户名';
COMMENT ON COLUMN users.password IS '密码';
COMMENT ON COLUMN users.real_name IS '真实姓名';
COMMENT ON COLUMN users.phone IS '手机号';
COMMENT ON COLUMN users.email IS '邮箱';
COMMENT ON COLUMN users.role IS '角色：ADMIN-管理员，SENIOR_LAWYER-主办律师，JUNIOR_LAWYER-辅助律师，ASSISTANT-律师助理，ADMIN_STAFF-行政人员';
COMMENT ON COLUMN users.tenant_id IS '租户ID';
COMMENT ON COLUMN users.avatar IS '头像URL';
COMMENT ON COLUMN users.status IS '状态：0-禁用，1-启用';
COMMENT ON COLUMN users.last_login_time IS '最后登录时间';
COMMENT ON COLUMN users.last_login_ip IS '最后登录IP';

-- 创建索引
CREATE INDEX idx_user_tenant ON users(tenant_id);
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_user_phone ON users(phone);

-- ==========================================
-- 案件表
-- ==========================================
CREATE TABLE IF NOT EXISTS cases (
    id BIGSERIAL PRIMARY KEY,
    case_number VARCHAR(100) COMMENT '案号',
    case_type VARCHAR(50) NOT NULL COMMENT '案件类型',
    case_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '案件状态',
    title VARCHAR(200) NOT NULL COMMENT '案件标题',
    plaintiff JSON COMMENT '原告信息',
    defendant JSON COMMENT '被告信息',
    claim_amount DECIMAL(12,2) COMMENT '标的金额',
    dispute_focus TEXT[] COMMENT '争议焦点',
    lawyer_id BIGINT COMMENT '承办律师ID',
    assistant_id BIGINT COMMENT '助理律师ID',
    tenant_id BIGINT NOT NULL COMMENT '租户ID',
    timeline JSON COMMENT '时间线',
    ai_analysis JSON COMMENT 'AI分析结果',
    description TEXT COMMENT '案件描述',
    filed_date DATE COMMENT '立案日期',
    closed_date DATE COMMENT '结案日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted INTEGER DEFAULT 0,
    CONSTRAINT fk_case_lawyer FOREIGN KEY (lawyer_id) REFERENCES users(id),
    CONSTRAINT fk_case_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

COMMENT ON TABLE cases IS '案件表';
COMMENT ON COLUMN cases.id IS '主键ID';
COMMENT ON COLUMN cases.case_number IS '案号';
COMMENT ON COLUMN cases.case_type IS '案件类型：LABOR_CONTRACT-劳动合同，WAGE-工资，INJURY-工伤，SOCIAL_INSURANCE-社保，TERMINATION-解除劳动关系，DISCRIMINATION-歧视，OTHER-其他';
COMMENT ON COLUMN cases.case_status IS '案件状态：PENDING-待立案，ARBITRATION-仲裁中，FIRST_APPEAL-一审，SECOND_APPEAL-二审，RETRIAL-再审，EXECUTION-执行中，CLOSED-已结案，CANCELLED-已撤销';
COMMENT ON COLUMN cases.title IS '案件标题';
COMMENT ON COLUMN cases.plaintiff IS '原告信息JSON';
COMMENT ON COLUMN cases.defendant IS '被告信息JSON';
COMMENT ON COLUMN cases.claim_amount IS '标的金额';
COMMENT ON COLUMN cases.dispute_focus IS '争议焦点';
COMMENT ON COLUMN cases.lawyer_id IS '承办律师ID';
COMMENT ON COLUMN cases.assistant_id IS '助理律师ID';
COMMENT ON COLUMN cases.tenant_id IS '租户ID';
COMMENT ON COLUMN cases.timeline IS '时间线JSON';
COMMENT ON COLUMN cases.ai_analysis IS 'AI分析结果JSON';
COMMENT ON COLUMN cases.description IS '案件描述';

-- 创建索引
CREATE INDEX idx_case_tenant ON cases(tenant_id);
CREATE INDEX idx_case_lawyer ON cases(lawyer_id);
CREATE INDEX idx_case_status ON cases(case_status);
CREATE INDEX idx_case_type ON cases(case_type);

-- ==========================================
-- 文书表
-- ==========================================
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    case_id BIGINT COMMENT '关联案件ID',
    doc_type VARCHAR(50) NOT NULL COMMENT '文书类型',
    title VARCHAR(200) NOT NULL COMMENT '文书标题',
    content TEXT COMMENT '文书内容',
    template_id BIGINT COMMENT '模板ID',
    version INTEGER DEFAULT 1 COMMENT '版本号',
    status VARCHAR(20) DEFAULT 'DRAFT' COMMENT '文书状态',
    ai_suggestions JSON COMMENT 'AI建议',
    tenant_id BIGINT NOT NULL COMMENT '租户ID',
    created_by BIGINT COMMENT '创建人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER DEFAULT 0,
    CONSTRAINT fk_doc_case FOREIGN KEY (case_id) REFERENCES cases(id),
    CONSTRAINT fk_doc_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

COMMENT ON TABLE documents IS '文书表';
COMMENT ON COLUMN documents.id IS '主键ID';
COMMENT ON COLUMN documents.case_id IS '关联案件ID';
COMMENT ON COLUMN documents.doc_type IS '文书类型';
COMMENT ON COLUMN documents.title IS '文书标题';
COMMENT ON COLUMN documents.content IS '文书内容';
COMMENT ON COLUMN documents.template_id IS '模板ID';
COMMENT ON COLUMN documents.version IS '版本号';
COMMENT ON COLUMN documents.status IS '文书状态：DRAFT-草稿，REVIEW-审核中，FINAL-定稿，ARCHIVED-归档';
COMMENT ON COLUMN documents.ai_suggestions IS 'AI建议JSON';
COMMENT ON COLUMN documents.tenant_id IS '租户ID';

-- 创建索引
CREATE INDEX idx_doc_case ON documents(case_id);
CREATE INDEX idx_doc_tenant ON documents(tenant_id);
CREATE INDEX idx_doc_type ON documents(doc_type);

-- ==========================================
-- 文书模板表
-- ==========================================
CREATE TABLE IF NOT EXISTS document_templates (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    doc_type VARCHAR(50) NOT NULL COMMENT '文书类型',
    content TEXT NOT NULL COMMENT '模板内容',
    variables JSON COMMENT '变量定义',
    category VARCHAR(50) COMMENT '分类',
    description VARCHAR(500) COMMENT '描述',
    is_public INTEGER DEFAULT 0 COMMENT '是否公开：0-否，1-是',
    tenant_id BIGINT COMMENT '租户ID（空表示系统模板）',
    use_count INTEGER DEFAULT 0 COMMENT '使用次数',
    rating DECIMAL(2,1) DEFAULT 0 COMMENT '评分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted INTEGER DEFAULT 0
);

COMMENT ON TABLE document_templates IS '文书模板表';
COMMENT ON COLUMN document_templates.id IS '主键ID';
COMMENT ON COLUMN document_templates.name IS '模板名称';
COMMENT ON COLUMN document_templates.doc_type IS '文书类型';
COMMENT ON COLUMN document_templates.content IS '模板内容';
COMMENT ON COLUMN document_templates.variables IS '变量定义JSON';
COMMENT ON COLUMN document_templates.category IS '分类';
COMMENT ON COLUMN document_templates.description IS '描述';
COMMENT ON COLUMN document_templates.is_public IS '是否公开：0-否，1-是';
COMMENT ON COLUMN document_templates.tenant_id IS '租户ID（空表示系统模板）';
COMMENT ON COLUMN document_templates.use_count IS '使用次数';
COMMENT ON COLUMN document_templates.rating IS '评分';

-- ==========================================
-- 知识库表
-- ==========================================
CREATE TABLE IF NOT EXISTS knowledge_base (
    id BIGSERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL COMMENT '分类',
    doc_type VARCHAR(20) NOT NULL COMMENT '文档类型：LAW-法规，CASE-案例，INTERNAL-内部资料',
    title VARCHAR(500) NOT NULL COMMENT '标题',
    content TEXT COMMENT '内容',
    source VARCHAR(200) COMMENT '来源',
    publish_date DATE COMMENT '发布日期',
    effective_date DATE COMMENT '生效日期',
    expiry_date DATE COMMENT '失效日期',
    tags TEXT[] COMMENT '标签',
    metadata JSON COMMENT '元数据',
    view_count INTEGER DEFAULT 0 COMMENT '查看次数',
    favorite_count INTEGER DEFAULT 0 COMMENT '收藏次数',
    tenant_id BIGINT COMMENT '租户ID（空表示公共知识库）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted INTEGER DEFAULT 0
);

COMMENT ON TABLE knowledge_base IS '知识库表';
COMMENT ON COLUMN knowledge_base.id IS '主键ID';
COMMENT ON COLUMN knowledge_base.category IS '分类';
COMMENT ON COLUMN knowledge_base.doc_type IS '文档类型：LAW-法规，CASE-案例，INTERNAL-内部资料';
COMMENT ON COLUMN knowledge_base.title IS '标题';
COMMENT ON COLUMN knowledge_base.content IS '内容';
COMMENT ON COLUMN knowledge_base.source IS '来源';
COMMENT ON COLUMN knowledge_base.publish_date IS '发布日期';
COMMENT ON COLUMN knowledge_base.effective_date IS '生效日期';
COMMENT ON COLUMN knowledge_base.expiry_date IS '失效日期';
COMMENT ON COLUMN knowledge_base.tags IS '标签';
COMMENT ON COLUMN knowledge_base.metadata IS '元数据JSON';
COMMENT ON COLUMN knowledge_base.view_count IS '查看次数';
COMMENT ON COLUMN knowledge_base.favorite_count IS '收藏次数';
COMMENT ON COLUMN knowledge_base.tenant_id IS '租户ID（空表示公共知识库）';

-- 创建索引
CREATE INDEX idx_kb_category ON knowledge_base(category);
CREATE INDEX idx_kb_type ON knowledge_base(doc_type);
CREATE INDEX idx_kb_tenant ON knowledge_base(tenant_id);

-- ==========================================
-- 聊天会话表
-- ==========================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    title VARCHAR(200) COMMENT '会话标题',
    case_id BIGINT COMMENT '关联案件ID',
    tenant_id BIGINT NOT NULL COMMENT '租户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER DEFAULT 0,
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_session_case FOREIGN KEY (case_id) REFERENCES cases(id),
    CONSTRAINT fk_session_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

COMMENT ON TABLE chat_sessions IS '聊天会话表';
COMMENT ON COLUMN chat_sessions.id IS '主键ID';
COMMENT ON COLUMN chat_sessions.user_id IS '用户ID';
COMMENT ON COLUMN chat_sessions.title IS '会话标题';
COMMENT ON COLUMN chat_sessions.case_id IS '关联案件ID';
COMMENT ON COLUMN chat_sessions.tenant_id IS '租户ID';

-- ==========================================
-- 聊天消息表
-- ==========================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL COMMENT '会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色：user-用户，assistant-助手',
    content TEXT NOT NULL COMMENT '消息内容',
    tokens INTEGER COMMENT 'Token数',
    metadata JSON COMMENT '元数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_message_session FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

COMMENT ON TABLE chat_messages IS '聊天消息表';
COMMENT ON COLUMN chat_messages.id IS '主键ID';
COMMENT ON COLUMN chat_messages.session_id IS '会话ID';
COMMENT ON COLUMN chat_messages.role IS '角色：user-用户，assistant-助手';
COMMENT ON COLUMN chat_messages.content IS '消息内容';
COMMENT ON COLUMN chat_messages.tokens IS 'Token数';
COMMENT ON COLUMN chat_messages.metadata IS '元数据JSON';

-- 创建索引
CREATE INDEX idx_msg_session ON chat_messages(session_id);

-- ==========================================
-- 证据表
-- ==========================================
CREATE TABLE IF NOT EXISTS evidences (
    id BIGSERIAL PRIMARY KEY,
    case_id BIGINT NOT NULL COMMENT '案件ID',
    name VARCHAR(200) NOT NULL COMMENT '证据名称',
    type VARCHAR(50) COMMENT '证据类型',
    description TEXT COMMENT '证据描述',
    file_url VARCHAR(500) COMMENT '文件URL',
    file_type VARCHAR(50) COMMENT '文件类型',
    file_size BIGINT COMMENT '文件大小',
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    chain_order INTEGER COMMENT '证据链顺序',
    chain_description TEXT COMMENT '证据链说明',
    tenant_id BIGINT NOT NULL COMMENT '租户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    is_deleted INTEGER DEFAULT 0,
    CONSTRAINT fk_evidence_case FOREIGN KEY (case_id) REFERENCES cases(id),
    CONSTRAINT fk_evidence_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

COMMENT ON TABLE evidences IS '证据表';
COMMENT ON COLUMN evidences.id IS '主键ID';
COMMENT ON COLUMN evidences.case_id IS '案件ID';
COMMENT ON COLUMN evidences.name IS '证据名称';
COMMENT ON COLUMN evidences.type IS '证据类型';
COMMENT ON COLUMN evidences.description IS '证据描述';
COMMENT ON COLUMN evidences.file_url IS '文件URL';
COMMENT ON COLUMN evidences.file_type IS '文件类型';
COMMENT ON COLUMN evidences.file_size IS '文件大小';
COMMENT ON COLUMN evidences.upload_time IS '上传时间';
COMMENT ON COLUMN evidences.chain_order IS '证据链顺序';
COMMENT ON COLUMN evidences.chain_description IS '证据链说明';
COMMENT ON COLUMN evidences.tenant_id IS '租户ID';

-- ==========================================
-- 计算记录表
-- ==========================================
CREATE TABLE IF NOT EXISTS calculations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    case_id BIGINT COMMENT '案件ID',
    calc_type VARCHAR(50) NOT NULL COMMENT '计算类型',
    input_params JSON NOT NULL COMMENT '输入参数',
    result JSON NOT NULL COMMENT '计算结果',
    tenant_id BIGINT NOT NULL COMMENT '租户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_calc_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_calc_case FOREIGN KEY (case_id) REFERENCES cases(id),
    CONSTRAINT fk_calc_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

COMMENT ON TABLE calculations IS '计算记录表';
COMMENT ON COLUMN calculations.id IS '主键ID';
COMMENT ON COLUMN calculations.user_id IS '用户ID';
COMMENT ON COLUMN calculations.case_id IS '案件ID';
COMMENT ON COLUMN calculations.calc_type IS '计算类型：ILLEGAL_TERMINATION-违法解除，OVERTIME-加班费，ANNUAL_LEAVE-年休假，INJURY-工伤赔偿';
COMMENT ON COLUMN calculations.input_params IS '输入参数JSON';
COMMENT ON COLUMN calculations.result IS '计算结果JSON';
COMMENT ON COLUMN calculations.tenant_id IS '租户ID';

-- ==========================================
-- 初始化数据
-- ==========================================

-- 插入默认租户（律所）
INSERT INTO tenants (name, code, contact_person, contact_phone, status, max_users, current_user_count)
VALUES ('示例律师事务所', 'DEMO_LAW_FIRM', '张经理', '13800138000', 1, 50, 1);

-- 插入默认管理员用户（密码：admin123，已使用BCrypt加密）
INSERT INTO users (username, password, real_name, phone, email, role, tenant_id, status)
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVKIUi', '系统管理员', '13800138001', 'admin@lawfirm.com', 'ADMIN', 1, 1);

-- 插入示例律师用户
INSERT INTO users (username, password, real_name, phone, email, role, tenant_id, status)
VALUES ('lawyer01', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVKIUi', '李律师', '13800138002', 'lawyer01@lawfirm.com', 'SENIOR_LAWYER', 1, 1);

-- 插入示例文书模板
INSERT INTO document_templates (name, doc_type, content, category, description, is_public)
VALUES
('劳动仲裁申请书模板', 'ARBITRATION_APPLICATION', '劳动人事争议仲裁申请书\n\n申请人：{{applicant_name}}，{{applicant_gender}}，{{applicant_birth_date}}出生，住{{applicant_address}}\n\n被申请人：{{respondent_name}}\n住所地：{{respondent_address}}\n法定代表人：{{respondent_legal_person}}\n\n仲裁请求：\n{{#each claims}}\n{{this}}\n{{/each}}\n\n事实与理由：\n{{facts}}\n\n此致\n{{arbitration_commission}}\n\n申请人：\n日期：', '劳动争议', '劳动仲裁申请书标准模板', 1),
('民事起诉状模板', 'CIVIL_COMPLAINT', '民事起诉状\n\n原告：{{plaintiff_name}}，{{plaintiff_gender}}，{{plaintiff_birth_date}}出生，住{{plaintiff_address}}\n\n被告：{{defendant_name}}\n住所地：{{defendant_address}}\n\n诉讼请求：\n{{#each claims}}\n{{this}}\n{{/each}}\n\n事实与理由：\n{{facts}}\n\n此致\n{{court}}\n\n原告：\n日期：', '民事诉讼', '民事起诉状标准模板', 1);
