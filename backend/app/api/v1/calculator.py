from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.calculator import CalculationRequest, CalculationResponse
from app.services.calculator_service import calculate

router = APIRouter(prefix="/calculator", tags=["calculator"])


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_compensation(
    req: CalculationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = calculate(req.calc_type, req.params)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CalculationResponse(
        result=result.result,
        breakdown=result.breakdown,
        basis=result.basis,
        steps=result.steps,
    )
