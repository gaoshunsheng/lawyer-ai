from __future__ import annotations

import uuid
from pydantic import BaseModel


class CaseTypeStat(BaseModel):
    type: str
    count: int
    amount: float


class CaseStatusStat(BaseModel):
    status: str
    count: int


class CaseOverviewResponse(BaseModel):
    total: int
    by_type: list[CaseTypeStat]
    by_status: list[CaseStatusStat]
    avg_duration_days: float
    win_rate: float
    total_claim_amount: float


class TrendPeriod(BaseModel):
    period: str
    total: int
    by_type: dict[str, int]
    avg_amount: float


class TrendsResponse(BaseModel):
    periods: list[TrendPeriod]


class LawyerStat(BaseModel):
    user_id: str
    name: str
    total_cases: int
    win_rate: float
    avg_satisfaction: float
    total_claim_amount: float


class LawyerPerformanceResponse(BaseModel):
    lawyers: list[LawyerStat]
    period_days: int


class ClientCaseSummary(BaseModel):
    id: str
    title: str
    status: str
    claim_amount: float | None
    created_at: str


class ClientReportResponse(BaseModel):
    client_name: str
    summary: dict
    cases: list[ClientCaseSummary]
