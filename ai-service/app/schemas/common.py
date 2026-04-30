from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = Field(default=0, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Optional[T] = Field(default=None, description="数据")
    request_id: Optional[str] = Field(default=None, description="请求ID")


class PageInfo(BaseModel):
    """分页信息"""
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total: int = Field(description="总数")
    total_pages: int = Field(description="总页数")


class PagedResponseModel(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = Field(default=0, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Optional["PagedData[T]"] = Field(default=None, description="数据")
    request_id: Optional[str] = Field(default=None, description="请求ID")


class PagedData(BaseModel, Generic[T]):
    """分页数据"""
    list: List[T] = Field(description="数据列表")
    pagination: PageInfo = Field(description="分页信息")


class ErrorDetail(BaseModel):
    """错误详情"""
    field: str = Field(description="字段")
    message: str = Field(description="错误消息")


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int = Field(description="状态码")
    message: str = Field(description="错误消息")
    errors: Optional[List[ErrorDetail]] = Field(default=None, description="错误详情")
    request_id: Optional[str] = Field(default=None, description="请求ID")


# ==================== 认证相关 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=100)


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=100)
    real_name: str = Field(..., description="真实姓名", min_length=1, max_length=50)
    phone: Optional[str] = Field(default=None, description="手机号", max_length=20)
    email: Optional[str] = Field(default=None, description="邮箱", max_length=100)
    role: Optional[str] = Field(default="ASSISTANT", description="角色")
    tenant_id: Optional[int] = Field(default=None, description="租户ID")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., description="新密码", min_length=6, max_length=100)


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间(秒)")


class UserInfo(BaseModel):
    """用户信息"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    real_name: Optional[str] = Field(default=None, description="真实姓名")
    phone: Optional[str] = Field(default=None, description="手机号")
    email: Optional[str] = Field(default=None, description="邮箱")
    role: Optional[str] = Field(default=None, description="角色")
    role_name: Optional[str] = Field(default=None, description="角色名称")
    tenant_id: Optional[int] = Field(default=None, description="租户ID")
    tenant_name: Optional[str] = Field(default=None, description="租户名称")
    avatar: Optional[str] = Field(default=None, description="头像URL")
    status: Optional[int] = Field(default=None, description="状态")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间(秒)")
    user_info: Optional[UserInfo] = Field(default=None, description="用户信息")


# ==================== 案件相关 ====================

class CaseCreate(BaseModel):
    """创建案件请求"""
    case_name: str = Field(..., description="案件名称", min_length=1, max_length=200)
    case_type: str = Field(..., description="案件类型")
    internal_number: Optional[str] = Field(default=None, description="内部编号", max_length=100)
    court: Optional[str] = Field(default=None, description="受理机构", max_length=100)
    client_type: str = Field(..., description="委托人类型")
    client_name: str = Field(..., description="委托人名称", min_length=1, max_length=100)
    client_id_number: Optional[str] = Field(default=None, description="委托人证件号", max_length=50)
    client_phone: Optional[str] = Field(default=None, description="委托人电话", max_length=20)
    client_address: Optional[str] = Field(default=None, description="委托人地址", max_length=200)
    opposing_party_name: Optional[str] = Field(default=None, description="对方当事人名称", max_length=100)
    opposing_party_id_number: Optional[str] = Field(default=None, description="对方证件号", max_length=50)
    opposing_party_phone: Optional[str] = Field(default=None, description="对方电话", max_length=20)
    opposing_party_address: Optional[str] = Field(default=None, description="对方地址", max_length=200)
    claim_amount: Optional[float] = Field(default=None, description="标的金额", ge=0)
    claim_items: Optional[List[dict]] = Field(default=None, description="诉讼请求")
    dispute_focus: Optional[List[str]] = Field(default=None, description="争议焦点")
    case_summary: Optional[str] = Field(default=None, description="案件摘要")
    lawyer_id: int = Field(..., description="主办律师ID")
    assistant_id: Optional[int] = Field(default=None, description="助理ID")
    accepted_at: Optional[str] = Field(default=None, description="委托日期")


class CaseUpdate(BaseModel):
    """更新案件请求"""
    case_name: Optional[str] = Field(default=None, description="案件名称", min_length=1, max_length=200)
    case_type: Optional[str] = Field(default=None, description="案件类型")
    case_status: Optional[str] = Field(default=None, description="案件状态")
    internal_number: Optional[str] = Field(default=None, description="内部编号", max_length=100)
    court: Optional[str] = Field(default=None, description="受理机构", max_length=100)
    client_name: Optional[str] = Field(default=None, description="委托人名称", max_length=100)
    claim_amount: Optional[float] = Field(default=None, description="标的金额", ge=0)
    dispute_focus: Optional[List[str]] = Field(default=None, description="争议焦点")
    case_summary: Optional[str] = Field(default=None, description="案件摘要")


class CaseListQuery(BaseModel):
    """案件列表查询"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(default=None, description="关键词")
    case_status: Optional[str] = Field(default=None, description="案件状态")
    case_type: Optional[str] = Field(default=None, description="案件类型")
    lawyer_id: Optional[int] = Field(default=None, description="律师ID")


# ==================== AI对话相关 ====================

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(description="角色: user/assistant/system")
    content: str = Field(description="消息内容")
    created_at: datetime = Field(description="创建时间")


class ChatRequest(BaseModel):
    """聊天请求"""
    content: str = Field(..., description="消息内容", min_length=1, max_length=10000)
    session_id: Optional[str] = Field(default=None, description="会话ID")
    case_id: Optional[int] = Field(default=None, description="关联案件ID")
    attachments: Optional[List[dict]] = Field(default=None, description="附件")
    stream: bool = Field(default=False, description="是否流式输出")


class ChatResponse(BaseModel):
    """聊天响应"""
    id: str = Field(description="消息ID")
    role: str = Field(description="角色")
    content: str = Field(description="消息内容")
    content_type: str = Field(default="text", description="内容类型")
    legal_basis: Optional[List[dict]] = Field(default=None, description="法律依据")
    cases_referenced: Optional[List[dict]] = Field(default=None, description="引用案例")
    tokens_used: Optional[int] = Field(default=None, description="消耗Token数")
    created_at: datetime = Field(description="创建时间")


# ==================== 文书相关 ====================

class DocumentCreate(BaseModel):
    """创建文书请求"""
    template_id: int = Field(..., description="模板ID")
    case_id: Optional[int] = Field(default=None, description="关联案件ID")
    title: str = Field(..., description="文书标题", min_length=1, max_length=200)
    variables: dict = Field(default_factory=dict, description="变量值")


class DocumentGenerate(BaseModel):
    """AI生成文书请求"""
    template_id: int = Field(..., description="模板ID")
    case_id: int = Field(..., description="案件ID")
    generate_options: Optional[dict] = Field(default=None, description="生成选项")


# ==================== 计算器相关 ====================

class IllegalTerminationCalc(BaseModel):
    """违法解除赔偿计算请求"""
    entry_date: str = Field(..., description="入职日期 YYYY-MM-DD")
    leave_date: str = Field(..., description="解除日期 YYYY-MM-DD")
    monthly_salary: float = Field(..., description="月工资", gt=0)
    average_salary_12m: Optional[float] = Field(default=None, description="12个月平均工资")
    city: Optional[str] = Field(default=None, description="城市")
    options: Optional[dict] = Field(default=None, description="计算选项")


class CalcResult(BaseModel):
    """计算结果"""
    input: dict = Field(description="输入参数")
    calculation: dict = Field(description="计算过程")
    result: dict = Field(description="计算结果")
    breakdown: List[dict] = Field(description="详细计算")
    legal_basis: List[dict] = Field(description="法律依据")
