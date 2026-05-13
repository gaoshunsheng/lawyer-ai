import datetime
import uuid

from pydantic import BaseModel


class TokenUsageResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    department_id: uuid.UUID | None
    user_id: uuid.UUID
    model_provider: str
    model_name: str
    agent_type: str | None
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int | None
    cost_cny: float | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class TokenUsageDailyResponse(BaseModel):
    date: datetime.date
    tenant_id: uuid.UUID
    department_id: uuid.UUID | None
    user_id: uuid.UUID | None
    model_name: str
    agent_type: str | None
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_cny: float | None
    request_count: int

    model_config = {"from_attributes": True}


class BudgetStatus(BaseModel):
    entity_type: str  # user/department/tenant
    entity_id: uuid.UUID
    budget: int | None
    used: int
    remaining: int | None
    percentage: float | None


class ModelConfigResponse(BaseModel):
    id: uuid.UUID
    provider_id: uuid.UUID
    model_name: str
    model_type: str
    capability: str | None
    input_price_per_m: float | None
    output_price_per_m: float | None
    max_tokens: int | None
    is_default: bool
    status: str

    model_config = {"from_attributes": True}
