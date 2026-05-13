from pydantic import BaseModel


class CalculationRequest(BaseModel):
    calc_type: str  # illegal_termination/overtime/annual_leave/work_injury
    params: dict


class CalculationStep(BaseModel):
    description: str
    formula: str | None = None


class CalculationResponse(BaseModel):
    result: float
    breakdown: dict
    basis: list[str]
    steps: list[str]
