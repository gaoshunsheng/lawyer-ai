from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel, Field


TRIAL_MODES = ("arbitration", "first_instance", "defense", "judgment")
TRIAL_ROLES = ("plaintiff", "defendant", "judge")


class TrialStartRequest(BaseModel):
    mode: str = Field(..., pattern="^(arbitration|first_instance|defense|judgment)$")
    role: str = Field(..., pattern="^(plaintiff|defendant|judge)$")


class TrialRespondRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class TrialSimulationResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    mode: str
    role: str
    status: str
    rounds_completed: int
    dispute_focus: list | None
    strategy_report: dict | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class TrialRoundResponse(BaseModel):
    id: uuid.UUID
    simulation_id: uuid.UUID
    round_num: int
    role: str
    content: str
    argument_strength: str | None
    evaluation: dict | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class StrategyReportResponse(BaseModel):
    dispute_focus: list[dict]
    argument_evaluation: list[dict]
    risk_points: list[dict]
    strategy_suggestions: list[dict]
    evidence_suggestions: list[dict]
