-- ==========================================
-- 文件表
-- ==========================================
CREATE TABLE IF NOT EXISTS files (
    id BIGSERIAL PRIMARY KEY,
    original_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    stored_name VARCHAR(255) NOT NULL COMMENT '存储文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_url VARCHAR(500) COMMENT '文件URL',
    file_type VARCHAR(100) COMMENT '文件类型',
    file_extension VARCHAR(20) COMMENT '文件扩展名',
    file_size BIGINT COMMENT '文件大小（字节）',
    category VARCHAR(50) COMMENT '文件分类',
    related_id BIGINT COMMENT '关联ID',
    related_type VARCHAR(50) COMMENT '关联类型',
    tenant_id BIGINT COMMENT '租户ID',
    description VARCHAR(500) COMMENT '描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted INTEGER DEFAULT 0
);

COMMENT ON TABLE files IS '文件表';
COMMENT ON COLUMN files.id IS '主键ID';
COMMENT ON COLUMN files.original_name IS '原始文件名';
COMMENT ON COLUMN files.stored_name IS '存储文件名';
COMMENT ON COLUMN files.file_path IS '文件路径';
COMMENT ON COLUMN files.file_url IS '文件URL';
COMMENT ON COLUMN files.file_type IS '文件类型（MIME类型）';
COMMENT ON COLUMN files.file_extension IS '文件扩展名';
COMMENT ON COLUMN files.file_size IS '文件大小（字节）';
COMMENT ON COLUMN files.category IS '文件分类：evidence-证据，document-文书，avatar-头像';
COMMENT ON COLUMN files.related_id IS '关联ID（案件ID、文书ID等）';
COMMENT ON COLUMN files.related_type IS '关联类型：case-案件，document-文书，evidence-证据';
COMMENT ON COLUMN files.tenant_id IS '租户ID';
COMMENT ON COLUMN files.description IS '描述';

-- 创建索引
CREATE INDEX idx_files_category ON files(category);
CREATE INDEX idx_files_related ON files(related_type, related_id);
CREATE INDEX idx_files_tenant ON files(tenant_id);

-- ==========================================
-- 时间线事件表
-- ==========================================
CREATE TABLE IF NOT EXISTS timeline_events (
    id BIGSERIAL PRIMARY KEY,
    case_id BIGINT NOT NULL COMMENT '案件ID',
    event_type VARCHAR(50) NOT NULL COMMENT '事件类型',
    title VARCHAR(200) NOT NULL COMMENT '事件标题',
    description TEXT COMMENT '事件描述',
    event_time TIMESTAMP NOT NULL COMMENT '事件时间',
    sort_order INTEGER DEFAULT 0 COMMENT '排序',
    attachments TEXT COMMENT '附件（JSON）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,
    is_deleted INTEGER DEFAULT 0,
    CONSTRAINT fk_timeline_case FOREIGN KEY (case_id) REFERENCES cases(id)
);

COMMENT ON TABLE timeline_events IS '时间线事件表';
COMMENT ON COLUMN timeline_events.id IS '主键ID';
COMMENT ON COLUMN timeline_events.case_id IS '案件ID';
COMMENT ON COLUMN timeline_events.event_type IS '事件类型：case_create-案件创建，case_update-案件更新，evidence_add-添加证据，document_create-创建文书，hearing-开庭，judgment-判决';
COMMENT ON COLUMN timeline_events.title IS '事件标题';
COMMENT ON COLUMN timeline_events.description IS '事件描述';
COMMENT ON COLUMN timeline_events.event_time IS '事件时间';
COMMENT ON COLUMN timeline_events.sort_order IS '排序';
COMMENT ON COLUMN timeline_events.attachments IS '附件（JSON）';

-- 创建索引
CREATE INDEX idx_timeline_case ON timeline_events(case_id);
CREATE INDEX idx_timeline_time ON timeline_events(event_time);

-- ==========================================
-- 操作日志表
-- ==========================================
CREATE TABLE IF NOT EXISTS operation_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT COMMENT '用户ID',
    username VARCHAR(50) COMMENT '用户名',
    tenant_id BIGINT COMMENT '租户ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_desc VARCHAR(500) COMMENT '操作描述',
    request_method VARCHAR(10) COMMENT '请求方法',
    request_url VARCHAR(500) COMMENT '请求URL',
    request_params TEXT COMMENT '请求参数',
    response_status INTEGER COMMENT '响应状态',
    response_time BIGINT COMMENT '响应时间（毫秒）',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent VARCHAR(500) COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE operation_logs IS '操作日志表';
COMMENT ON COLUMN operation_logs.id IS '主键ID';
COMMENT ON COLUMN operation_logs.user_id IS '用户ID';
COMMENT ON COLUMN operation_logs.username IS '用户名';
COMMENT ON COLUMN operation_logs.tenant_id IS '租户ID';
COMMENT ON COLUMN operation_logs.operation_type IS '操作类型：CREATE-创建，UPDATE-更新，DELETE-删除，VIEW-查看，LOGIN-登录，LOGOUT-登出';
COMMENT ON COLUMN operation_logs.operation_desc IS '操作描述';
COMMENT ON COLUMN operation_logs.request_method IS '请求方法：GET，POST，PUT，DELETE';
COMMENT ON COLUMN operation_logs.request_url IS '请求URL';
COMMENT ON COLUMN operation_logs.request_params IS '请求参数';
COMMENT ON COLUMN operation_logs.response_status IS '响应状态';
COMMENT ON COLUMN operation_logs.response_time IS '响应时间（毫秒）';
COMMENT ON COLUMN operation_logs.ip_address IS 'IP地址';
COMMENT ON COLUMN operation_logs.user_agent IS '用户代理';

-- 创建索引
CREATE INDEX idx_log_user ON operation_logs(user_id);
CREATE INDEX idx_log_tenant ON operation_logs(tenant_id);
CREATE INDEX idx_log_time ON operation_logs(created_at);
CREATE INDEX idx_log_type ON operation_logs(operation_type);

-- ==========================================
-- 计算记录表（已存在，更新）
-- ==========================================
-- 见之前的calculations表定义
