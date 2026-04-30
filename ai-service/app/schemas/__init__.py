"""
Schema包初始化
"""
from app.schemas.common import (
    ResponseModel, PagedResponseModel, PagedData, PageInfo,
    LoginRequest, RegisterRequest, RefreshTokenRequest, ChangePasswordRequest,
    TokenResponse, UserInfo, LoginResponse,
    CaseCreate, CaseUpdate, CaseListQuery,
    ChatMessage, ChatRequest, ChatResponse,
    DocumentCreate, DocumentGenerate,
    IllegalTerminationCalc, CalcResult
)
from app.schemas.chat import (
    ChatRequest as ChatRequestSchema,
    ChatResponse as ChatResponseSchema,
    SessionInfo, MessageInfo, LegalBasis, CaseReference,
    CreateSessionRequest
)

__all__ = [
    "ResponseModel", "PagedResponseModel", "PagedData", "PageInfo",
    "LoginRequest", "RegisterRequest", "RefreshTokenRequest", "ChangePasswordRequest",
    "TokenResponse", "UserInfo", "LoginResponse",
    "CaseCreate", "CaseUpdate", "CaseListQuery",
    "ChatMessage", "ChatRequest", "ChatResponse",
    "DocumentCreate", "DocumentGenerate",
    "IllegalTerminationCalc", "CalcResult",
    "ChatRequestSchema", "ChatResponseSchema",
    "SessionInfo", "MessageInfo", "LegalBasis", "CaseReference",
    "CreateSessionRequest"
]
