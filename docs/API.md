# 律师AI助手 - API接口文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | 律师AI助手 - 劳动法专业版 |
| API版本 | V1.0 |
| 基础路径 | https://api.lawyer-ai.com/v1 |
| 协议 | HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

---

## 一、接口规范

### 1.1 请求规范

#### 请求头 (Request Headers)

| Header | 必填 | 说明 |
|--------|------|------|
| Authorization | 是 | Bearer {access_token} |
| Content-Type | 是 | application/json |
| X-Tenant-Id | 是 | 租户ID |
| X-Request-Id | 否 | 请求追踪ID，用于日志追踪 |
| Accept-Language | 否 | 语言，默认 zh-CN |

#### 请求方式

| 方法 | 说明 |
|------|------|
| GET | 查询资源 |
| POST | 创建资源 |
| PUT | 更新资源（全量） |
| PATCH | 更新资源（部分） |
| DELETE | 删除资源 |

#### 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码，从1开始 |
| page_size | int | 20 | 每页数量，最大100 |
| sort_by | string | created_at | 排序字段 |
| sort_order | string | desc | 排序方向：asc/desc |

### 1.2 响应规范

#### 成功响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        // 业务数据
    },
    "request_id": "req_abc123"
}
```

#### 分页响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 100,
            "total_pages": 5
        }
    },
    "request_id": "req_abc123"
}
```

#### 错误响应

```json
{
    "code": 10001,
    "message": "参数错误",
    "errors": [
        {
            "field": "email",
            "message": "邮箱格式不正确"
        }
    ],
    "request_id": "req_abc123"
}
```

### 1.3 错误码定义

#### 通用错误码 (1xxxx)

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 10001 | 参数错误 |
| 10002 | 请求格式错误 |
| 10003 | 请求方法不支持 |
| 10004 | 请求频率超限 |

#### 认证错误码 (2xxxx)

| 错误码 | 说明 |
|--------|------|
| 20001 | 未登录 |
| 20002 | Token过期 |
| 20003 | Token无效 |
| 20004 | 权限不足 |
| 20005 | 账号已禁用 |
| 20006 | 账号已锁定 |

#### 业务错误码 (3xxxx)

| 错误码 | 说明 |
|--------|------|
| 30001 | 资源不存在 |
| 30002 | 资源已存在 |
| 30003 | 资源已删除 |
| 30004 | 操作不允许 |
| 30005 | 数据校验失败 |

#### 案件错误码 (4xxxx)

| 错误码 | 说明 |
|--------|------|
| 40001 | 案件不存在 |
| 40002 | 案件状态不允许此操作 |
| 40003 | 案件数量已达上限 |

#### 文书错误码 (5xxxx)

| 错误码 | 说明 |
|--------|------|
| 50001 | 文书不存在 |
| 50002 | 模板不存在 |
| 50003 | 文书生成失败 |

#### AI错误码 (6xxxx)

| 错误码 | 说明 |
|--------|------|
| 60001 | AI服务不可用 |
| 60002 | AI请求超时 |
| 60003 | AI响应错误 |
| 60004 | 内容审核不通过 |

#### 系统错误码 (9xxxx)

| 错误码 | 说明 |
|--------|------|
| 90001 | 系统繁忙 |
| 90002 | 服务不可用 |
| 90003 | 数据库错误 |
| 90004 | 缓存错误 |

---

## 二、认证模块

### 2.1 用户登录

**接口描述**：用户登录，获取访问令牌

**请求信息**：
- **URL**: `/auth/login`
- **Method**: `POST`
- **Auth**: 不需要

**请求参数**：

```json
{
    "email": "lawyer@example.com",
    "password": "Password123!",
    "remember_me": true
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |
| remember_me | boolean | 否 | 记住我，延长token有效期 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "refresh_token_string",
        "token_type": "Bearer",
        "expires_in": 7200,
        "user": {
            "id": 10001,
            "email": "lawyer@example.com",
            "name": "李律师",
            "avatar_url": "https://cdn.example.com/avatar.jpg",
            "title": "合伙人",
            "roles": ["lawyer", "admin"],
            "permissions": ["case:read", "case:write", "document:write"]
        }
    }
}
```

### 2.2 刷新令牌

**接口描述**：刷新访问令牌

**请求信息**：
- **URL**: `/auth/refresh`
- **Method**: `POST`
- **Auth**: 不需要

**请求参数**：

```json
{
    "refresh_token": "refresh_token_string"
}
```

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "token_type": "Bearer",
        "expires_in": 7200
    }
}
```

### 2.3 退出登录

**接口描述**：用户退出登录

**请求信息**：
- **URL**: `/auth/logout`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：无

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": null
}
```

### 2.4 获取当前用户信息

**接口描述**：获取当前登录用户的详细信息

**请求信息**：
- **URL**: `/auth/me`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：无

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 10001,
        "email": "lawyer@example.com",
        "name": "李律师",
        "avatar_url": "https://cdn.example.com/avatar.jpg",
        "phone": "13800138000",
        "title": "合伙人",
        "license_number": "13101202012345678",
        "status": "active",
        "roles": [
            {
                "id": 1,
                "name": "管理员",
                "code": "admin"
            }
        ],
        "permissions": [
            "case:read",
            "case:write",
            "case:delete",
            "document:read",
            "document:write"
        ],
        "settings": {
            "default_template": "arbitration_application",
            "notification_enabled": true
        },
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

### 2.5 修改密码

**接口描述**：修改当前用户密码

**请求信息**：
- **URL**: `/auth/password`
- **Method**: `PUT`
- **Auth**: 需要

**请求参数**：

```json
{
    "old_password": "OldPassword123!",
    "new_password": "NewPassword456!",
    "confirm_password": "NewPassword456!"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码，至少8位，包含大小写字母和数字 |
| confirm_password | string | 是 | 确认新密码 |

**响应示例**：

```json
{
    "code": 0,
    "message": "密码修改成功",
    "data": null
}
```

---

## 三、案件管理模块

### 3.1 获取案件列表

**接口描述**：获取案件列表，支持筛选、搜索、排序

**请求信息**：
- **URL**: `/cases`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| keyword | string | 否 | 关键词搜索（案件名称、案号、当事人） |
| case_status | string | 否 | 案件状态：pending/arbitration/first_appeal/second_appeal/closed |
| case_type | string | 否 | 案件类型 |
| lawyer_id | int | 否 | 承办律师ID |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| sort_by | string | 否 | 排序字段，默认created_at |
| sort_order | string | 否 | 排序方向：asc/desc，默认desc |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": 10001,
                "case_number": "(2024)沪0101民初12345号",
                "internal_number": "LAW-2024-001",
                "case_name": "张三与某科技公司劳动争议纠纷",
                "case_type": "labor_contract",
                "case_type_name": "劳动合同纠纷",
                "case_status": "arbitration",
                "case_status_name": "仲裁中",
                "case_stage": "仲裁阶段",
                "court": "上海市黄浦区劳动人事争议仲裁委员会",
                "client_type": "employee",
                "client_name": "张三",
                "opposing_party_name": "某科技公司",
                "claim_amount": 150000.00,
                "lawyer": {
                    "id": 100,
                    "name": "李律师"
                },
                "accepted_at": "2024-01-10",
                "filed_at": "2024-01-12",
                "next_event": {
                    "date": "2024-01-20",
                    "title": "开庭"
                },
                "created_at": "2024-01-10T10:00:00Z",
                "updated_at": "2024-01-15T14:30:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 156,
            "total_pages": 8
        }
    }
}
```

### 3.2 获取案件详情

**接口描述**：获取单个案件的详细信息

**请求信息**：
- **URL**: `/cases/{case_id}`
- **Method**: `GET`
- **Auth**: 需要

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| case_id | int | 是 | 案件ID |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 10001,
        "case_number": "(2024)沪0101民初12345号",
        "internal_number": "LAW-2024-001",
        "case_name": "张三与某科技公司劳动争议纠纷",
        "case_type": "labor_contract",
        "case_type_name": "劳动合同纠纷",
        "case_status": "arbitration",
        "case_status_name": "仲裁中",
        "case_stage": "仲裁阶段",
        "court": "上海市黄浦区劳动人事争议仲裁委员会",
        "judge": "王仲裁员",
        "client": {
            "type": "employee",
            "name": "张三",
            "id_number": "310101199001011234",
            "phone": "13800138001",
            "address": "上海市浦东新区xxx",
            "agent": "李律师"
        },
        "opposing_party": {
            "name": "某科技公司",
            "id_number": "91310000MA1K5LXXXX",
            "phone": "021-12345678",
            "address": "上海市浦东新区xxx",
            "agent": "王律师"
        },
        "claim_amount": 150000.00,
        "claim_items": [
            {
                "item": "违法解除劳动合同赔偿金",
                "amount": 132000.00
            },
            {
                "item": "加班费",
                "amount": 15000.00
            },
            {
                "item": "未休年休假工资",
                "amount": 3000.00
            }
        ],
        "dispute_focus": [
            "是否构成违法解除",
            "赔偿金计算标准",
            "加班费是否应支持"
        ],
        "case_summary": "申请人张三于2020年6月入职被申请人某科技公司...",
        "lawyer": {
            "id": 100,
            "name": "李律师"
        },
        "assistant": {
            "id": 101,
            "name": "张助理"
        },
        "team_members": [
            {
                "id": 100,
                "name": "李律师",
                "role": "主办律师"
            }
        ],
        "accepted_at": "2024-01-10",
        "filed_at": "2024-01-12",
        "closed_at": null,
        "case_result": null,
        "result_amount": null,
        "result_summary": null,
        "ai_analysis": {
            "advantages": [
                "公司规章制度未经民主程序，解除依据不足",
                "考勤记录显示无旷工行为",
                "有录音证明解除时未说明具体理由"
            ],
            "risks": [
                "加班费主张缺乏加班审批记录",
                "年休假已休部分需进一步核实"
            ],
            "strategies": [
                "重点收集公司规章制度公示证据",
                "补充收集领导安排加班的聊天记录",
                "申请证人出庭作证"
            ],
            "win_probability": 0.78,
            "similar_cases_count": 127
        },
        "created_at": "2024-01-10T10:00:00Z",
        "updated_at": "2024-01-15T14:30:00Z"
    }
}
```

### 3.3 创建案件

**接口描述**：创建新案件

**请求信息**：
- **URL**: `/cases`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "case_name": "张三与某科技公司劳动争议纠纷",
    "case_type": "labor_contract",
    "internal_number": "LAW-2024-001",
    "court": "上海市黄浦区劳动人事争议仲裁委员会",
    "client_type": "employee",
    "client_name": "张三",
    "client_id_number": "310101199001011234",
    "client_phone": "13800138001",
    "client_address": "上海市浦东新区xxx",
    "opposing_party_name": "某科技公司",
    "opposing_party_id_number": "91310000MA1K5LXXXX",
    "opposing_party_phone": "021-12345678",
    "opposing_party_address": "上海市浦东新区xxx",
    "claim_amount": 150000.00,
    "claim_items": [
        {
            "item": "违法解除劳动合同赔偿金",
            "amount": 132000.00
        }
    ],
    "dispute_focus": [
        "是否构成违法解除"
    ],
    "case_summary": "案件摘要...",
    "lawyer_id": 100,
    "assistant_id": 101,
    "accepted_at": "2024-01-10"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| case_name | string | 是 | 案件名称 |
| case_type | string | 是 | 案件类型 |
| internal_number | string | 否 | 内部编号 |
| court | string | 否 | 受理机构 |
| client_type | string | 是 | 委托人类型：employee/employer |
| client_name | string | 是 | 委托人名称 |
| client_id_number | string | 否 | 委托人证件号 |
| client_phone | string | 否 | 委托人电话 |
| client_address | string | 否 | 委托人地址 |
| opposing_party_name | string | 否 | 对方当事人名称 |
| opposing_party_id_number | string | 否 | 对方证件号 |
| opposing_party_phone | string | 否 | 对方电话 |
| opposing_party_address | string | 否 | 对方地址 |
| claim_amount | number | 否 | 标的金额 |
| claim_items | array | 否 | 诉讼请求列表 |
| dispute_focus | array | 否 | 争议焦点 |
| case_summary | string | 否 | 案件摘要 |
| lawyer_id | int | 是 | 主办律师ID |
| assistant_id | int | 否 | 助理ID |
| accepted_at | string | 否 | 委托日期 |

**响应示例**：

```json
{
    "code": 0,
    "message": "案件创建成功",
    "data": {
        "id": 10001,
        "case_number": null,
        "internal_number": "LAW-2024-001",
        "case_name": "张三与某科技公司劳动争议纠纷",
        "case_status": "pending",
        "created_at": "2024-01-10T10:00:00Z"
    }
}
```

### 3.4 更新案件

**接口描述**：更新案件信息

**请求信息**：
- **URL**: `/cases/{case_id}`
- **Method**: `PUT`
- **Auth**: 需要

**请求参数**：同创建案件，所有字段均为可选

**响应示例**：

```json
{
    "code": 0,
    "message": "案件更新成功",
    "data": {
        "id": 10001,
        "updated_at": "2024-01-15T14:30:00Z"
    }
}
```

### 3.5 删除案件

**接口描述**：删除案件（软删除）

**请求信息**：
- **URL**: `/cases/{case_id}`
- **Method**: `DELETE`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "案件删除成功",
    "data": null
}
```

### 3.6 获取案件时间线

**接口描述**：获取案件时间线事件列表

**请求信息**：
- **URL**: `/cases/{case_id}/timeline`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| case_id | int | 是 | 案件ID |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": 1,
                "event_date": "2024-01-20",
                "event_time": "09:30:00",
                "event_type": "hearing",
                "event_type_name": "开庭",
                "event_title": "第一次开庭",
                "event_content": "在仲裁委第一仲裁庭开庭审理",
                "is_key_event": true,
                "reminder_at": "2024-01-19T09:00:00Z",
                "reminder_sent": true,
                "attachments": [
                    {
                        "name": "开庭通知.pdf",
                        "url": "https://cdn.example.com/xxx.pdf"
                    }
                ],
                "created_at": "2024-01-10T10:00:00Z"
            },
            {
                "id": 2,
                "event_date": "2024-01-15",
                "event_time": null,
                "event_type": "evidence_submit",
                "event_type_name": "举证",
                "event_title": "举证期限届满",
                "event_content": "提交证据材料5份",
                "is_key_event": true,
                "reminder_at": null,
                "reminder_sent": false,
                "attachments": [],
                "created_at": "2024-01-10T10:00:00Z"
            }
        ]
    }
}
```

### 3.7 添加时间线事件

**接口描述**：添加案件时间线事件

**请求信息**：
- **URL**: `/cases/{case_id}/timeline`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "event_date": "2024-01-20",
    "event_time": "09:30:00",
    "event_type": "hearing",
    "event_title": "第一次开庭",
    "event_content": "在仲裁委第一仲裁庭开庭审理",
    "is_key_event": true,
    "reminder_at": "2024-01-19T09:00:00Z",
    "attachments": [
        {
            "name": "开庭通知.pdf",
            "url": "https://cdn.example.com/xxx.pdf"
        }
    ]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| event_date | string | 是 | 事件日期，格式 YYYY-MM-DD |
| event_time | string | 否 | 事件时间，格式 HH:mm:ss |
| event_type | string | 是 | 事件类型 |
| event_title | string | 是 | 事件标题 |
| event_content | string | 否 | 事件内容 |
| is_key_event | boolean | 否 | 是否关键事件，默认false |
| reminder_at | string | 否 | 提醒时间 |
| attachments | array | 否 | 附件列表 |

**事件类型枚举**：

| 值 | 名称 |
|------|------|
| accept | 委托 |
| file | 立案 |
| hearing | 开庭 |
| evidence_submit | 举证 |
| evidence_exchange | 证据交换 |
| mediation | 调解 |
| judgment | 裁判 |
| appeal | 上诉 |
| execute | 执行 |
| close | 结案 |
| other | 其他 |

**响应示例**：

```json
{
    "code": 0,
    "message": "事件添加成功",
    "data": {
        "id": 1,
        "event_date": "2024-01-20",
        "event_title": "第一次开庭",
        "created_at": "2024-01-10T10:00:00Z"
    }
}
```

### 3.8 获取案件证据列表

**接口描述**：获取案件证据列表

**请求信息**：
- **URL**: `/cases/{case_id}/evidences`
- **Method**: `GET`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": 1,
                "evidence_number": "证据1",
                "evidence_name": "劳动合同",
                "evidence_type": "contract",
                "evidence_type_name": "合同",
                "evidence_category": "本证",
                "source": "原告提供",
                "obtain_date": "2024-01-10",
                "page_count": 5,
                "description": "2020年6月签订的劳动合同",
                "prove_purpose": "证明劳动关系及工资标准",
                "is_original": true,
                "file_url": "https://cdn.example.com/xxx.pdf",
                "file_name": "劳动合同.pdf",
                "file_size": 1024000,
                "file_type": "application/pdf",
                "display_order": 1,
                "created_at": "2024-01-10T10:00:00Z"
            }
        ]
    }
}
```

### 3.9 上传证据

**接口描述**：上传案件证据

**请求信息**：
- **URL**: `/cases/{case_id}/evidences`
- **Method**: `POST`
- **Auth**: 需要
- **Content-Type**: `multipart/form-data`

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 证据文件 |
| evidence_name | string | 是 | 证据名称 |
| evidence_type | string | 是 | 证据类型 |
| evidence_category | string | 否 | 证据分类：本证/反证 |
| source | string | 否 | 证据来源 |
| obtain_date | string | 否 | 获取日期 |
| description | string | 否 | 证据说明 |
| prove_purpose | string | 否 | 证明目的 |
| is_original | boolean | 否 | 是否原件，默认true |

**响应示例**：

```json
{
    "code": 0,
    "message": "证据上传成功",
    "data": {
        "id": 1,
        "evidence_number": "证据1",
        "evidence_name": "劳动合同",
        "file_url": "https://cdn.example.com/xxx.pdf",
        "ocr_text": "OCR识别文本...",
        "ai_summary": "AI生成的证据摘要...",
        "created_at": "2024-01-10T10:00:00Z"
    }
}
```

### 3.10 AI案件分析

**接口描述**：对案件进行AI分析，识别优劣势、风险点、策略建议

**请求信息**：
- **URL**: `/cases/{case_id}/analyze`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "force_refresh": false
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| force_refresh | boolean | 否 | 是否强制刷新分析结果 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "case_id": 10001,
        "advantages": [
            {
                "content": "公司规章制度未经民主程序，解除依据不足",
                "evidence_ids": [1, 3],
                "legal_basis": ["劳动合同法第4条"]
            },
            {
                "content": "考勤记录显示无旷工行为",
                "evidence_ids": [2],
                "legal_basis": []
            }
        ],
        "risks": [
            {
                "content": "加班费主张缺乏加班审批记录",
                "level": "medium",
                "suggestion": "补充收集领导安排加班的聊天记录"
            }
        ],
        "strategies": [
            {
                "content": "重点收集公司规章制度公示证据",
                "priority": "high"
            },
            {
                "content": "申请证人出庭作证",
                "priority": "medium"
            }
        ],
        "win_probability": 0.78,
        "similar_cases": [
            {
                "case_id": "ext_12345",
                "case_number": "(2023)沪01民终12345号",
                "similarity": 0.85,
                "result": "plaintiff_win"
            }
        ],
        "analyzed_at": "2024-01-15T14:30:00Z"
    }
}
```

---

## 四、文书管理模块

### 4.1 获取文书模板列表

**接口描述**：获取文书模板列表

**请求信息**：
- **URL**: `/document-templates`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 模板分类 |
| keyword | string | 否 | 关键词搜索 |
| is_public | boolean | 否 | 是否公开模板 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": 1,
                "name": "劳动争议仲裁申请书",
                "code": "arbitration_application",
                "category": "application",
                "category_name": "申请类",
                "description": "劳动争议仲裁申请书标准模板",
                "is_system": true,
                "is_public": true,
                "use_count": 1234,
                "rating": 4.8,
                "tags": ["劳动争议", "仲裁", "申请书"],
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 50,
            "total_pages": 3
        }
    }
}
```

### 4.2 获取文书模板详情

**接口描述**：获取文书模板详情，包含模板内容和变量定义

**请求信息**：
- **URL**: `/document-templates/{template_id}`
- **Method**: `GET`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "name": "劳动争议仲裁申请书",
        "code": "arbitration_application",
        "category": "application",
        "description": "劳动争议仲裁申请书标准模板",
        "content": "# 劳动人事争议仲裁申请书\n\n## 申请人\n姓名：{{applicant_name}}\n性别：{{applicant_gender}}\n...",
        "variables": [
            {
                "name": "applicant_name",
                "label": "申请人姓名",
                "type": "text",
                "required": true,
                "default_value": "",
                "source": "case.client_name",
                "description": "申请人姓名"
            },
            {
                "name": "applicant_gender",
                "label": "申请人性别",
                "type": "select",
                "required": true,
                "options": ["男", "女"],
                "default_value": "男"
            },
            {
                "name": "claim_amount",
                "label": "标的金额",
                "type": "number",
                "required": true,
                "source": "case.claim_amount",
                "format": "currency"
            }
        ],
        "format_rules": {
            "font_family": "宋体",
            "font_size": 12,
            "line_height": 1.5,
            "margins": {
                "top": 2.54,
                "bottom": 2.54,
                "left": 3.17,
                "right": 3.17
            }
        },
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

### 4.3 获取文书列表

**接口描述**：获取文书列表

**请求信息**：
- **URL**: `/documents`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| case_id | int | 否 | 案件ID |
| doc_type | string | 否 | 文书类型 |
| status | string | 否 | 状态 |
| keyword | string | 否 | 关键词 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": 1,
                "case_id": 10001,
                "case_name": "张三与某科技公司劳动争议纠纷",
                "template_id": 1,
                "template_name": "劳动争议仲裁申请书",
                "doc_type": "arbitration_application",
                "doc_type_name": "仲裁申请书",
                "title": "张三-仲裁申请书-2024-01-15",
                "status": "draft",
                "status_name": "草稿",
                "version": 3,
                "word_count": 2345,
                "created_by": {
                    "id": 100,
                    "name": "李律师"
                },
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T14:30:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 30,
            "total_pages": 2
        }
    }
}
```

### 4.4 创建文书

**接口描述**：创建新文书

**请求信息**：
- **URL**: `/documents`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "template_id": 1,
    "case_id": 10001,
    "title": "张三-仲裁申请书-2024-01-15",
    "variables": {
        "applicant_name": "张三",
        "applicant_gender": "男",
        "applicant_birth": "1990年1月1日",
        "applicant_nationality": "汉族",
        "applicant_id_number": "310101199001011234",
        "applicant_address": "上海市浦东新区xxx路xxx号",
        "applicant_phone": "13800138001",
        "respondent_name": "某科技公司",
        "respondent_address": "上海市浦东新区张江高科技园区xxx号",
        "respondent_legal_representative": "李四",
        "claim_items": [
            {
                "content": "请求裁决被申请人支付违法解除劳动合同赔偿金人民币132,000元"
            },
            {
                "content": "请求裁决被申请人支付加班费人民币15,000元"
            }
        ],
        "facts_and_reasons": "申请人于2020年6月1日入职被申请人处..."
    }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_id | int | 是 | 模板ID |
| case_id | int | 否 | 关联案件ID |
| title | string | 是 | 文书标题 |
| variables | object | 是 | 变量值 |

**响应示例**：

```json
{
    "code": 0,
    "message": "文书创建成功",
    "data": {
        "id": 1,
        "title": "张三-仲裁申请书-2024-01-15",
        "content": "# 劳动人事争议仲裁申请书\n\n...",
        "html_content": "<html>...</html>",
        "ai_suggestions": [
            {
                "type": "warning",
                "field": "claim_items[1].content",
                "message": "加班费计算基数建议明确为'基本工资+岗位绩效'",
                "legal_basis": "(2023)沪01民终12345号"
            }
        ],
        "status": "draft",
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

### 4.5 获取文书详情

**接口描述**：获取文书详情

**请求信息**：
- **URL**: `/documents/{document_id}`
- **Method**: `GET`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "case_id": 10001,
        "case_name": "张三与某科技公司劳动争议纠纷",
        "template_id": 1,
        "template_name": "劳动争议仲裁申请书",
        "doc_type": "arbitration_application",
        "title": "张三-仲裁申请书-2024-01-15",
        "content": "# 劳动人事争议仲裁申请书\n\n...",
        "html_content": "<html>...</html>",
        "variables": {
            "applicant_name": "张三",
            "applicant_gender": "男"
        },
        "ai_suggestions": [
            {
                "id": "sug_001",
                "type": "warning",
                "field": "claim_items[1].content",
                "position": {
                    "start": 500,
                    "end": 600
                },
                "message": "加班费计算基数建议明确为'基本工资+岗位绩效'",
                "legal_basis": "(2023)沪01民终12345号",
                "accepted": false
            }
        ],
        "status": "draft",
        "version": 3,
        "word_count": 2345,
        "file_url": "https://cdn.example.com/doc/xxx.docx",
        "file_name": "张三-仲裁申请书-2024-01-15.docx",
        "created_by": {
            "id": 100,
            "name": "李律师"
        },
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T14:30:00Z"
    }
}
```

### 4.6 更新文书内容

**接口描述**：更新文书内容

**请求信息**：
- **URL**: `/documents/{document_id}`
- **Method**: `PUT`
- **Auth**: 需要

**请求参数**：

```json
{
    "title": "张三-仲裁申请书-2024-01-15（修改版）",
    "content": "更新后的内容...",
    "html_content": "更新后的HTML...",
    "variables": {
        "applicant_name": "张三",
        "applicant_gender": "男"
    }
}
```

**响应示例**：

```json
{
    "code": 0,
    "message": "文书更新成功",
    "data": {
        "id": 1,
        "version": 4,
        "ai_suggestions": [
            {
                "id": "sug_002",
                "type": "info",
                "message": "检测到新的优化建议..."
            }
        ],
        "updated_at": "2024-01-15T15:00:00Z"
    }
}
```

### 4.7 AI生成文书内容

**接口描述**：根据案件信息AI生成文书内容

**请求信息**：
- **URL**: `/documents/generate`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "template_id": 1,
    "case_id": 10001,
    "generate_options": {
        "include_legal_basis": true,
        "include_case_reference": true,
        "detail_level": "high"
    }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_id | int | 是 | 模板ID |
| case_id | int | 是 | 案件ID |
| generate_options | object | 否 | 生成选项 |
| generate_options.include_legal_basis | boolean | 否 | 是否包含法条引用，默认true |
| generate_options.include_case_reference | boolean | 否 | 是否包含案例引用，默认true |
| generate_options.detail_level | string | 否 | 详细程度：low/medium/high，默认medium |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "content": "# 劳动人事争议仲裁申请书\n\n## 申请人\n姓名：张三\n性别：男\n...\n\n## 仲裁请求\n一、请求裁决被申请人支付违法解除劳动合同赔偿金人民币132,000元；\n\n二、请求裁决被申请人支付加班费人民币15,000元；\n\n三、请求裁决被申请人支付未休年休假工资人民币3,000元。\n\n## 事实与理由\n申请人于2020年6月1日入职被申请人处，担任软件工程师一职...\n\n## 法律依据\n根据《中华人民共和国劳动合同法》第三十九条、第四十七条、第四十八条、第八十七条之规定...",
        "variables": {
            "applicant_name": "张三",
            "applicant_gender": "男",
            "claim_items": [...],
            "facts_and_reasons": "..."
        },
        "legal_basis": [
            {
                "law_name": "中华人民共和国劳动合同法",
                "article": "第三十九条",
                "content": "劳动者有下列情形之一的，用人单位可以解除劳动合同..."
            }
        ],
        "referenced_cases": [
            {
                "case_number": "(2023)沪01民终12345号",
                "similarity": 0.85
            }
        ],
        "generated_at": "2024-01-15T10:00:00Z"
    }
}
```

### 4.8 导出文书

**接口描述**：导出文书为指定格式

**请求信息**：
- **URL**: `/documents/{document_id}/export`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "format": "docx",
    "include_header_footer": true,
    "include_page_number": true
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 是 | 导出格式：docx/pdf/html |
| include_header_footer | boolean | 否 | 是否包含页眉页脚，默认true |
| include_page_number | boolean | 否 | 是否包含页码，默认true |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "file_url": "https://cdn.example.com/export/xxx.docx",
        "file_name": "张三-仲裁申请书-2024-01-15.docx",
        "file_size": 51200,
        "expires_at": "2024-01-16T10:00:00Z"
    }
}
```

### 4.9 获取文书版本历史

**接口描述**：获取文书的版本历史

**请求信息**：
- **URL**: `/documents/{document_id}/versions`
- **Method**: `GET`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": 3,
                "document_id": 1,
                "version": 3,
                "change_summary": "修改了仲裁请求部分",
                "created_by": {
                    "id": 100,
                    "name": "李律师"
                },
                "created_at": "2024-01-15T14:30:00Z"
            },
            {
                "id": 2,
                "document_id": 1,
                "version": 2,
                "change_summary": "补充了事实与理由部分",
                "created_by": {
                    "id": 100,
                    "name": "李律师"
                },
                "created_at": "2024-01-15T12:00:00Z"
            }
        ]
    }
}
```

### 4.10 接受AI建议

**接口描述**：接受AI建议并应用到文书

**请求信息**：
- **URL**: `/documents/{document_id}/suggestions/{suggestion_id}/accept`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "modified_content": "修改后的内容（可选）"
}
```

**响应示例**：

```json
{
    "code": 0,
    "message": "建议已应用",
    "data": {
        "document_id": 1,
        "version": 5,
        "updated_at": "2024-01-15T16:00:00Z"
    }
}
```

---

## 五、智能咨询模块

### 5.1 创建对话会话

**接口描述**：创建新的对话会话

**请求信息**：
- **URL**: `/chat/sessions`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "case_id": 10001,
    "title": "张三案件咨询"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| case_id | int | 否 | 关联案件ID |
| title | string | 否 | 会话标题 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": "sess_abc123",
        "title": "张三案件咨询",
        "case_id": 10001,
        "status": "active",
        "message_count": 0,
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

### 5.2 获取对话会话列表

**接口描述**：获取用户的对话会话列表

**请求信息**：
- **URL**: `/chat/sessions`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |
| status | string | 否 | 状态：active/archived |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": "sess_abc123",
                "title": "张三案件咨询",
                "case_id": 10001,
                "case_name": "张三与某科技公司劳动争议纠纷",
                "status": "active",
                "message_count": 5,
                "last_message": {
                    "role": "assistant",
                    "content": "根据您描述的情况...",
                    "created_at": "2024-01-15T14:30:00Z"
                },
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T14:30:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 10,
            "total_pages": 1
        }
    }
}
```

### 5.3 发送消息（AI问答）

**接口描述**：发送消息并获取AI回复

**请求信息**：
- **URL**: `/chat/sessions/{session_id}/messages`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "content": "用户申请劳动仲裁，主张违法解除赔偿金，公司辩称严重违纪解除，但只有一份口头警告记录，请问胜诉概率？",
    "attachments": [
        {
            "name": "解除劳动合同通知书.pdf",
            "url": "https://cdn.example.com/xxx.pdf"
        }
    ],
    "stream": false
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 消息内容 |
| attachments | array | 否 | 附件列表 |
| stream | boolean | 否 | 是否流式输出，默认false |

**响应示例（非流式）**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": "msg_xyz789",
        "role": "assistant",
        "content": "根据您描述的情况，分析如下：\n\n**【法律依据】**\n\n1. 《劳动合同法》第39条：劳动者严重违纪，用人单位可单方解除劳动合同\n2. 《劳动合同法》第48条：违法解除的救济途径\n\n**【关键事实分析】**\n\n1. 口头警告记录证明力较弱\n2. 需确认公司规章制度是否经过民主程序\n3. 需核实解除通知是否送达及送达方式\n\n**【胜诉概率评估】** ⭐⭐⭐⭐ (较高)\n\n理由：用人单位负举证责任，仅有口头警告难以证明\"严重违纪\"\n\n**【类似案例参考】**\n\n- (2023)沪01民终12345号 - 支持劳动者\n- (2022)京02民终6789号 - 支持劳动者",
        "content_type": "markdown",
        "legal_basis": [
            {
                "law_id": 1,
                "law_name": "中华人民共和国劳动合同法",
                "article": "第三十九条",
                "content": "劳动者有下列情形之一的，用人单位可以解除劳动合同...",
                "url": "/laws/1/articles/39"
            },
            {
                "law_id": 1,
                "law_name": "中华人民共和国劳动合同法",
                "article": "第四十八条",
                "content": "用人单位违反本法规定解除或者终止劳动合同...",
                "url": "/laws/1/articles/48"
            }
        ],
        "cases_referenced": [
            {
                "case_id": "ext_12345",
                "case_number": "(2023)沪01民终12345号",
                "case_name": "张三与某科技公司劳动争议纠纷",
                "similarity": 0.85,
                "result": "plaintiff_win"
            }
        ],
        "tokens_used": 1250,
        "latency": 2500,
        "created_at": "2024-01-15T14:30:00Z"
    }
}
```

**响应示例（流式）**：

流式响应使用 Server-Sent Events (SSE)，Content-Type 为 `text/event-stream`。

```
event: message
data: {"type": "content", "delta": "根据您描述的"}

event: message
data: {"type": "content", "delta": "情况，分析如下："}

event: message
data: {"type": "legal_basis", "data": {"law_name": "劳动合同法", "article": "第39条"}}

event: message
data: {"type": "content", "delta": "\n\n**【法律依据】**"}

event: done
data: {"tokens_used": 1250}
```

### 5.4 获取对话历史

**接口描述**：获取对话会话的消息历史

**请求信息**：
- **URL**: `/chat/sessions/{session_id}/messages`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量，最大50 |
| order | string | 否 | 排序：asc/desc，默认asc |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": "msg_001",
                "role": "user",
                "content": "用户申请劳动仲裁，主张违法解除赔偿金...",
                "attachments": [],
                "created_at": "2024-01-15T14:00:00Z"
            },
            {
                "id": "msg_002",
                "role": "assistant",
                "content": "根据您描述的情况，分析如下...",
                "content_type": "markdown",
                "legal_basis": [...],
                "cases_referenced": [...],
                "feedback": "helpful",
                "created_at": "2024-01-15T14:00:05Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 2,
            "total_pages": 1
        }
    }
}
```

### 5.5 消息反馈

**接口描述**：对AI回复进行反馈

**请求信息**：
- **URL**: `/chat/messages/{message_id}/feedback`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "feedback": "helpful",
    "content": "回答很专业，对我很有帮助"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| feedback | string | 是 | 反馈类型：helpful/not_helpful |
| content | string | 否 | 反馈内容 |

**响应示例**：

```json
{
    "code": 0,
    "message": "感谢您的反馈",
    "data": null
}
```

### 5.6 导出对话记录

**接口描述**：导出对话记录为指定格式

**请求信息**：
- **URL**: `/chat/sessions/{session_id}/export`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "format": "docx",
    "include_legal_basis": true,
    "include_cases": true
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 是 | 导出格式：docx/pdf/md |
| include_legal_basis | boolean | 否 | 是否包含法条引用，默认true |
| include_cases | boolean | 否 | 是否包含案例引用，默认true |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "file_url": "https://cdn.example.com/export/chat_xxx.docx",
        "file_name": "法律咨询记录-2024-01-15.docx",
        "file_size": 30720,
        "expires_at": "2024-01-16T14:30:00Z"
    }
}
```

---

## 六、知识库模块

### 6.1 法规检索

**接口描述**：检索法规

**请求信息**：
- **URL**: `/laws`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 关键词 |
| law_type | string | 否 | 法规类型 |
| category | string | 否 | 分类 |
| status | string | 否 | 效力状态：effective/expired/revised |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": 1,
                "law_type": "law",
                "law_type_name": "法律",
                "name": "中华人民共和国劳动合同法",
                "short_name": "劳动合同法",
                "issuing_authority": "全国人民代表大会常务委员会",
                "publish_date": "2007-06-29",
                "effective_date": "2008-01-01",
                "status": "effective",
                "status_name": "现行有效",
                "category": "劳动法",
                "summary": "为了完善劳动合同制度，明确劳动合同双方当事人的权利和义务...",
                "view_count": 12345,
                "cite_count": 6789,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 500,
            "total_pages": 25
        }
    }
}
```

### 6.2 获取法规详情

**接口描述**：获取法规详情

**请求信息**：
- **URL**: `/laws/{law_id}`
- **Method**: `GET`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "law_type": "law",
        "law_type_name": "法律",
        "name": "中华人民共和国劳动合同法",
        "short_name": "劳动合同法",
        "issuing_authority": "全国人民代表大会常务委员会",
        "document_number": "主席令第六十五号",
        "publish_date": "2007-06-29",
        "effective_date": "2008-01-01",
        "expiry_date": null,
        "status": "effective",
        "status_name": "现行有效",
        "category": "劳动法",
        "tags": ["劳动合同", "劳动关系", "劳动者权益"],
        "content": "第一章 总则\n\n第一条 为了完善劳动合同制度...",
        "summary": "为了完善劳动合同制度，明确劳动合同双方当事人的权利和义务...",
        "ai_interpretation": "《劳动合同法》是规范劳动合同制度的基本法律...",
        "source_url": "http://www.npc.gov.cn/...",
        "view_count": 12345,
        "cite_count": 6789,
        "articles": [
            {
                "id": 1,
                "article_number": "第一条",
                "article_title": "立法目的",
                "content": "为了完善劳动合同制度，明确劳动合同双方当事人的权利和义务...",
                "ai_interpretation": "本条规定了劳动合同法的立法目的..."
            }
        ],
        "related_laws": [
            {
                "id": 2,
                "name": "中华人民共和国劳动法"
            }
        ],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

### 6.3 获取法条详情

**接口描述**：获取法条详情

**请求信息**：
- **URL**: `/laws/{law_id}/articles/{article_number}`
- **Method**: `GET`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 39,
        "law_id": 1,
        "law_name": "中华人民共和国劳动合同法",
        "article_number": "第三十九条",
        "article_title": "用人单位单方解除劳动合同（过失性辞退）",
        "content": "劳动者有下列情形之一的，用人单位可以解除劳动合同：\n（一）在试用期间被证明不符合录用条件的；\n（二）严重违反用人单位的规章制度的；\n（三）严重失职，营私舞弊，给用人单位造成重大损害的；\n（四）劳动者同时与其他用人单位建立劳动关系，对完成本单位的工作任务造成严重影响，或者经用人单位提出，拒不改正的；\n（五）因本法第二十六条第一款第一项规定的情形致使劳动合同无效的；\n（六）被依法追究刑事责任的。",
        "ai_interpretation": "本条规定了用人单位可以单方解除劳动合同的情形...\n\n**适用要点：**\n1. 用人单位负举证责任\n2. 规章制度必须经过民主程序\n3. 需要达到\"严重\"程度",
        "related_articles": [
            {
                "law_id": 1,
                "article_number": "第四十条",
                "article_title": "无过失性辞退"
            }
        ],
        "related_cases_count": 234,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

### 6.4 案例检索

**接口描述**：检索案例

**请求信息**：
- **URL**: `/precedent-cases`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 关键词 |
| case_type | string | 否 | 案件类型 |
| court | string | 否 | 法院 |
| court_level | string | 否 | 法院层级 |
| procedure_type | string | 否 | 程序类型 |
| judgment_result | string | 否 | 裁判结果 |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "list": [
            {
                "id": "ext_12345",
                "case_number": "(2023)沪01民终12345号",
                "case_name": "张三与某科技公司劳动争议纠纷二审民事判决书",
                "court": "上海市第一中级人民法院",
                "court_level": "intermediate",
                "court_level_name": "中级人民法院",
                "case_type": "labor_contract",
                "case_type_name": "劳动合同纠纷",
                "procedure_type": "second_appeal",
                "procedure_type_name": "二审",
                "judge_date": "2023-08-15",
                "judgment_result": "plaintiff_win",
                "judgment_result_name": "劳动者胜诉",
                "dispute_focus": [
                    "用人单位以劳动者严重违纪为由解除劳动合同，但仅有口头警告记录，是否构成违法解除"
                ],
                "summary": "法院认为，用人单位主张劳动者严重违纪，应当承担举证责任...",
                "view_count": 1234,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 1000,
            "total_pages": 50
        }
    }
}
```

### 6.5 获取案例详情

**接口描述**：获取案例详情

**请求信息**：
- **URL**: `/precedent-cases/{case_id}`
- **Method**: `GET`
- **Auth**: 需要

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": "ext_12345",
        "case_number": "(2023)沪01民终12345号",
        "case_name": "张三与某科技公司劳动争议纠纷二审民事判决书",
        "court": "上海市第一中级人民法院",
        "court_level": "intermediate",
        "court_level_name": "中级人民法院",
        "case_type": "labor_contract",
        "case_type_name": "劳动合同纠纷",
        "procedure_type": "second_appeal",
        "procedure_type_name": "二审",
        "judge_date": "2023-08-15",
        "publish_date": "2023-09-01",
        "plaintiff": "张三",
        "defendant": "某科技公司",
        "plaintiff_agent": "李律师",
        "defendant_agent": "王律师",
        "claim": "请求撤销一审判决，改判...",
        "fact_found": "经审理查明，上诉人张三于2020年6月入职被上诉人某科技公司...",
        "court_opinion": "本院认为，用人单位主张劳动者严重违纪，应当承担举证责任...",
        "judgment": "驳回上诉，维持原判...",
        "full_text": "完整判决书内容...",
        "dispute_focus": [
            "用人单位以劳动者严重违纪为由解除劳动合同，但仅有口头警告记录，是否构成违法解除"
        ],
        "legal_basis": [
            {
                "law_name": "中华人民共和国劳动合同法",
                "article": "第三十九条",
                "content": "劳动者有下列情形之一的..."
            }
        ],
        "judgment_result": "plaintiff_win",
        "judgment_result_name": "劳动者胜诉",
        "claim_supported": 0.85,
        "summary": "本案中，公司仅提供口头警告记录...",
        "key_points": {
            "focus": "严重违纪解除的举证责任",
            "ruling": "用人单位举证不能，构成违法解除",
            "reference_value": "对于仅有口头警告记录的违纪解除案件具有参考价值"
        },
        "view_count": 1234,
        "cite_count": 56,
        "source_url": "https://wenshu.court.gov.cn/...",
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

### 6.6 语义检索（法规+案例）

**接口描述**：基于语义相似度检索法规和案例

**请求信息**：
- **URL**: `/search/semantic`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "query": "用人单位以严重违纪为由解除劳动合同，但只有口头警告记录，是否构成违法解除",
    "types": ["law", "case"],
    "limit": 10
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 查询内容 |
| types | array | 否 | 检索类型：law/case，默认全部 |
| limit | int | 否 | 每类返回数量，默认10 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "laws": [
            {
                "id": 1,
                "name": "中华人民共和国劳动合同法",
                "article_number": "第三十九条",
                "content": "劳动者有下列情形之一的，用人单位可以解除劳动合同...",
                "similarity": 0.92,
                "highlight": "严重违反用人单位的<em>规章制度</em>的"
            }
        ],
        "cases": [
            {
                "id": "ext_12345",
                "case_number": "(2023)沪01民终12345号",
                "case_name": "张三与某科技公司劳动争议纠纷",
                "summary": "用人单位主张劳动者严重违纪，应当承担举证责任...",
                "similarity": 0.85,
                "highlight": "仅有<em>口头警告记录</em>，不足以证明严重违纪"
            }
        ]
    }
}
```

### 6.7 收藏知识

**接口描述**：收藏法规或案例

**请求信息**：
- **URL**: `/knowledge/favorites`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "target_type": "law",
    "target_id": 1,
    "folder": "劳动法常用",
    "notes": "劳动合同法第39条很重要",
    "tags": ["违法解除", "严重违纪"]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| target_type | string | 是 | 收藏类型：law/article/case |
| target_id | string | 是 | 目标ID |
| folder | string | 否 | 收藏夹名称 |
| notes | string | 否 | 笔记 |
| tags | array | 否 | 标签 |

**响应示例**：

```json
{
    "code": 0,
    "message": "收藏成功",
    "data": {
        "id": 1,
        "target_type": "law",
        "target_id": 1,
        "folder": "劳动法常用",
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

---

## 七、计算器模块

### 7.1 违法解除赔偿计算

**接口描述**：计算违法解除劳动合同赔偿金

**请求信息**：
- **URL**: `/calculator/illegal-termination`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "entry_date": "2020-06-01",
    "leave_date": "2024-01-15",
    "monthly_salary": 15000,
    "average_salary_12m": 16500,
    "city": "上海市",
    "options": {
        "high_salary_cap": true,
        "negotiated_termination": false,
        "severance_paid": false
    }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| entry_date | string | 是 | 入职日期，格式 YYYY-MM-DD |
| leave_date | string | 是 | 解除日期 |
| monthly_salary | number | 是 | 月工资 |
| average_salary_12m | number | 否 | 解除前12个月平均工资，默认取monthly_salary |
| city | string | 否 | 城市，用于获取社平工资 |
| options | object | 否 | 计算选项 |
| options.high_salary_cap | boolean | 否 | 是否适用高薪封顶，默认true |
| options.negotiated_termination | boolean | 否 | 是否协商解除，默认false |
| options.severance_paid | boolean | 否 | 是否已支付经济补偿，默认false |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "input": {
            "entry_date": "2020-06-01",
            "leave_date": "2024-01-15",
            "monthly_salary": 15000,
            "average_salary_12m": 16500,
            "city": "上海市"
        },
        "calculation": {
            "work_years": 3.54,
            "work_years_rounded": 4,
            "base_salary": 16500,
            "social_average_salary": 12183,
            "salary_cap_applied": false,
            "salary_cap_multiplier": 3,
            "salary_cap": 36549
        },
        "result": {
            "severance": 66000,
            "multiplier": 2,
            "total": 132000
        },
        "breakdown": [
            {
                "item": "工作年限",
                "value": "3年7个月",
                "note": "超过6个月按1年计算，计4年"
            },
            {
                "item": "计算基数",
                "value": "16,500元/月",
                "note": "解除前12个月平均工资"
            },
            {
                "item": "经济补偿金",
                "value": "66,000元",
                "formula": "16,500 × 4 = 66,000"
            },
            {
                "item": "赔偿倍数",
                "value": "2倍",
                "note": "违法解除按经济补偿金的2倍支付"
            },
            {
                "item": "违法解除赔偿金",
                "value": "132,000元",
                "formula": "66,000 × 2 = 132,000"
            }
        ],
        "legal_basis": [
            {
                "law_name": "中华人民共和国劳动合同法",
                "article": "第四十七条",
                "content": "经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付..."
            },
            {
                "law_name": "中华人民共和国劳动合同法",
                "article": "第八十七条",
                "content": "用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第四十七条规定的经济补偿标准的二倍向劳动者支付赔偿金。"
            }
        ],
        "city_data": {
            "city": "上海市",
            "year": 2023,
            "social_average_salary": 12183,
            "data_source": "上海市人力资源和社会保障局",
            "effective_date": "2024-07-01"
        },
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

### 7.2 加班费计算

**接口描述**：计算加班费

**请求信息**：
- **URL**: `/calculator/overtime`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "monthly_salary": 15000,
    "overtime_records": [
        {
            "date": "2024-01-06",
            "type": "weekend",
            "hours": 8,
            "compensated": false
        },
        {
            "date": "2024-01-13",
            "type": "weekend",
            "hours": 8,
            "compensated": false
        },
        {
            "date": "2024-01-01",
            "type": "holiday",
            "hours": 8,
            "compensated": false
        }
    ],
    "options": {
        "salary_base": "actual",
        "include_bonus": true
    }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| monthly_salary | number | 是 | 月工资 |
| overtime_records | array | 是 | 加班记录列表 |
| overtime_records[].date | string | 是 | 加班日期 |
| overtime_records[].type | string | 是 | 加班类型：workday/weekend/holiday |
| overtime_records[].hours | number | 是 | 加班时长（小时） |
| overtime_records[].compensated | boolean | 否 | 是否已调休，默认false |
| options | object | 否 | 计算选项 |
| options.salary_base | string | 否 | 工资基数：actual/minimum，默认actual |
| options.include_bonus | boolean | 否 | 是否包含奖金，默认true |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "input": {
            "monthly_salary": 15000,
            "overtime_records": [...]
        },
        "calculation": {
            "hourly_rate": 86.21,
            "formula": "15,000 ÷ 21.75 ÷ 8 = 86.21"
        },
        "result": {
            "workday_overtime": 0,
            "weekend_overtime": 1379.36,
            "holiday_overtime": 2069.04,
            "total": 3448.40
        },
        "breakdown": [
            {
                "date": "2024-01-06",
                "type": "weekend",
                "type_name": "休息日加班",
                "hours": 8,
                "rate": 200,
                "amount": 1379.36,
                "formula": "86.21 × 8 × 200% = 1379.36"
            },
            {
                "date": "2024-01-13",
                "type": "weekend",
                "type_name": "休息日加班",
                "hours": 8,
                "rate": 200,
                "amount": 1379.36,
                "formula": "86.21 × 8 × 200% = 1379.36"
            },
            {
                "date": "2024-01-01",
                "type": "holiday",
                "type_name": "法定节假日加班",
                "hours": 8,
                "rate": 300,
                "amount": 2069.04,
                "formula": "86.21 × 8 × 300% = 2069.04"
            }
        ],
        "legal_basis": [
            {
                "law_name": "中华人民共和国劳动法",
                "article": "第四十四条",
                "content": "有下列情形之一的，用人单位应当按照下列标准支付高于劳动者正常工作时间工资的工资报酬..."
            }
        ],
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

### 7.3 年休假工资计算

**接口描述**：计算未休年休假工资

**请求信息**：
- **URL**: `/calculator/annual-leave`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "work_years": 5,
    "annual_leave_entitled": 5,
    "annual_leave_taken": 2,
    "monthly_salary": 15000,
    "year": 2023
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| work_years | number | 是 | 累计工作年限 |
| annual_leave_entitled | number | 是 | 应休年休假天数 |
| annual_leave_taken | number | 是 | 已休年休假天数 |
| monthly_salary | number | 是 | 月工资 |
| year | number | 是 | 年度 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "input": {
            "work_years": 5,
            "annual_leave_entitled": 5,
            "annual_leave_taken": 2,
            "monthly_salary": 15000,
            "year": 2023
        },
        "calculation": {
            "daily_rate": 689.66,
            "formula": "15,000 ÷ 21.75 = 689.66"
        },
        "result": {
            "unpaid_days": 3,
            "compensation_rate": 300,
            "total": 6206.94
        },
        "breakdown": [
            {
                "item": "应休年休假",
                "value": "5天"
            },
            {
                "item": "已休年休假",
                "value": "2天"
            },
            {
                "item": "未休年休假",
                "value": "3天"
            },
            {
                "item": "日工资标准",
                "value": "689.66元",
                "formula": "15,000 ÷ 21.75 = 689.66"
            },
            {
                "item": "补偿标准",
                "value": "300%",
                "note": "未休年休假按日工资的300%支付"
            },
            {
                "item": "未休年休假工资",
                "value": "6,206.94元",
                "formula": "689.66 × 3 × 300% = 6,206.94"
            }
        ],
        "legal_basis": [
            {
                "law_name": "职工带薪年休假条例",
                "article": "第五条",
                "content": "单位确因工作需要不能安排职工休年休假的，经职工本人同意，可以不安排职工休年休假。对职工应休未休的年休假天数，单位应当按照该职工日工资收入的300%支付年休假工资报酬。"
            }
        ],
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

### 7.4 保存计算记录

**接口描述**：保存计算记录到案件

**请求信息**：
- **URL**: `/calculator/records`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "case_id": 10001,
    "calculation_type": "illegal_termination",
    "input_params": {
        "entry_date": "2020-06-01",
        "leave_date": "2024-01-15",
        "monthly_salary": 15000,
        "average_salary_12m": 16500,
        "city": "上海市"
    },
    "output_result": {
        "total": 132000,
        "severance": 66000,
        "multiplier": 2
    },
    "notes": "张三违法解除赔偿计算"
}
```

**响应示例**：

```json
{
    "code": 0,
    "message": "保存成功",
    "data": {
        "id": 1,
        "case_id": 10001,
        "calculation_type": "illegal_termination",
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

---

## 八、文件上传模块

### 8.1 获取上传凭证

**接口描述**：获取文件上传凭证（用于直传OSS）

**请求信息**：
- **URL**: `/upload/token`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "file_name": "劳动合同.pdf",
    "file_size": 1024000,
    "file_type": "application/pdf",
    "purpose": "evidence"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_name | string | 是 | 文件名 |
| file_size | number | 是 | 文件大小（字节） |
| file_type | string | 是 | MIME类型 |
| purpose | string | 是 | 用途：evidence/document/avatar等 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "upload_url": "https://bucket.oss-cn-shanghai.aliyuncs.com",
        "upload_method": "POST",
        "upload_params": {
            "key": "evidence/2024/01/xxx.pdf",
            "policy": "eyJleHBpcmF0aW9uIjoiMjAyNC0wMS0xNlQxMDowMDowMFoiLCJjb25kaXRpb25zIjpb...",
            "OSSAccessKeyId": "LTAI5xxx",
            "signature": "xxx",
            "success_action_status": "201"
        },
        "file_url": "https://cdn.example.com/evidence/2024/01/xxx.pdf",
        "expires_at": "2024-01-15T11:00:00Z"
    }
}
```

### 8.2 确认上传完成

**接口描述**：确认文件上传完成

**请求信息**：
- **URL**: `/upload/confirm`
- **Method**: `POST`
- **Auth**: 需要

**请求参数**：

```json
{
    "file_url": "https://cdn.example.com/evidence/2024/01/xxx.pdf",
    "file_name": "劳动合同.pdf",
    "file_size": 1024000,
    "file_type": "application/pdf",
    "purpose": "evidence"
}
```

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "file_id": "file_abc123",
        "file_url": "https://cdn.example.com/evidence/2024/01/xxx.pdf",
        "file_name": "劳动合同.pdf",
        "file_size": 1024000,
        "file_type": "application/pdf",
        "ocr_text": "OCR识别文本...",
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

---

## 九、系统设置模块

### 9.1 获取系统配置

**接口描述**：获取系统配置

**请求信息**：
- **URL**: `/settings`
- **Method**: `GET`
- **Auth**: 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keys | string | 否 | 配置键，多个用逗号分隔 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "ai_model": "gpt-4",
        "max_tokens_per_day": 100000,
        "max_cases": 1000,
        "max_storage": 10737418240,
        "notification_enabled": true,
        "theme": "light"
    }
}
```

### 9.2 更新用户设置

**接口描述**：更新当前用户的个人设置

**请求信息**：
- **URL**: `/settings/user`
- **Method**: `PUT`
- **Auth**: 需要

**请求参数**：

```json
{
    "default_template": "arbitration_application",
    "notification_enabled": true,
    "email_notification": true,
    "theme": "light"
}
```

**响应示例**：

```json
{
    "code": 0,
    "message": "设置更新成功",
    "data": null
}
```

---

## 十、通用模块

### 10.1 获取枚举值

**接口描述**：获取系统枚举值

**请求信息**：
- **URL**: `/enums/{type}`
- **Method**: `GET`
- **Auth**: 不需要

**路径参数**：

| 参数 | 说明 |
|------|------|
| type | 枚举类型：case_type/case_status/doc_type/court_level等 |

**响应示例**：

```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "value": "labor_contract",
            "label": "劳动合同纠纷"
        },
        {
            "value": "wage",
            "label": "劳动报酬纠纷"
        },
        {
            "value": "injury",
            "label": "工伤保险纠纷"
        },
        {
            "value": "social_insurance",
            "label": "社会保险纠纷"
        },
        {
            "value": "termination",
            "label": "解除劳动关系纠纷"
        }
    ]
}
```

### 10.2 健康检查

**接口描述**：检查服务健康状态

**请求信息**：
- **URL**: `/health`
- **Method**: `GET`
- **Auth**: 不需要

**响应示例**：

```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-01-15T10:00:00Z",
    "services": {
        "database": "healthy",
        "redis": "healthy",
        "milvus": "healthy",
        "ai_service": "healthy"
    }
}
```

---

## 十一、Webhook通知

### 11.1 Webhook事件

| 事件类型 | 说明 | 触发时机 |
|----------|------|----------|
| case.created | 案件创建 | 案件创建成功后 |
| case.status_changed | 案件状态变更 | 案件状态变更后 |
| case.timeline_added | 时间线事件添加 | 添加时间线事件后 |
| document.generated | 文书生成完成 | AI文书生成完成后 |
| chat.message.created | 对话消息创建 | AI回复完成后 |
| notification.created | 通知创建 | 有新通知时 |

### 11.2 Webhook载荷示例

```json
{
    "event_type": "case.status_changed",
    "event_id": "evt_abc123",
    "timestamp": "2024-01-15T10:00:00Z",
    "data": {
        "case_id": 10001,
        "old_status": "pending",
        "new_status": "arbitration",
        "changed_by": {
            "user_id": 100,
            "name": "李律师"
        }
    }
}
```

---

## 十二、限流策略

### 12.1 限流规则

| 接口类型 | 限流策略 | 说明 |
|----------|----------|------|
| 普通接口 | 100次/分钟/用户 | 案件、文书等CRUD操作 |
| AI对话 | 30次/分钟/用户 | 智能咨询对话 |
| 文书生成 | 10次/分钟/用户 | AI文书生成 |
| 文件上传 | 20次/分钟/用户 | 文件上传 |
| 搜索接口 | 60次/分钟/用户 | 知识库检索 |

### 12.2 限流响应

当触发限流时，返回 HTTP 429 状态码：

```json
{
    "code": 10004,
    "message": "请求频率超限，请稍后再试",
    "retry_after": 60,
    "request_id": "req_abc123"
}
```

---

## 十三、版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| V1.0 | 2024-01-15 | 初始版本 |

---

**文档结束**
