"""
赔偿计算器路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.schemas.common import ResponseModel
from app.services.calculator_service import CompensationCalculator

router = APIRouter()


class IllegalTerminationCalc(BaseModel):
    """违法解除赔偿计算请求"""
    entry_date: str = Field(..., description="入职日期 YYYY-MM-DD")
    leave_date: str = Field(..., description="解除日期 YYYY-MM-DD")
    monthly_salary: float = Field(..., description="月工资", gt=0)
    average_salary_12m: float = Field(None, description="12个月平均工资")
    city: str = Field(None, description="城市")
    high_salary_cap: bool = Field(False, description="是否适用高薪封顶")
    is_negotiated: bool = Field(False, description="是否协商解除")


class OvertimeCalc(BaseModel):
    """加班费计算请求"""
    monthly_salary: float = Field(..., description="月工资", gt=0)
    workday_hours: float = Field(0, description="工作日加班小时数", ge=0)
    weekend_hours: float = Field(0, description="休息日加班小时数", ge=0)
    holiday_hours: float = Field(0, description="法定节假日加班小时数", ge=0)
    work_days_per_month: float = Field(21.75, description="每月工作天数", gt=0)


class AnnualLeaveCalc(BaseModel):
    """年休假工资计算请求"""
    monthly_salary: float = Field(..., description="月工资", gt=0)
    total_work_years: float = Field(..., description="累计工作年限", ge=0)
    unused_days: float = Field(..., description="未休年休假天数", ge=0)
    work_days_per_month: float = Field(21.75, description="每月工作天数", gt=0)


@router.post("/illegal-termination", response_model=ResponseModel)
async def calc_illegal_termination(request: IllegalTerminationCalc):
    """
    违法解除劳动合同赔偿计算

    计算公式：
    - 经济补偿金 = 工作年限 × 月工资
    - 违法解除赔偿金 = 经济补偿金 × 2

    注意事项：
    - 工作年限不满6个月的按0.5年计算，满6个月的按1年计算
    - 月工资高于社平工资3倍的，按社平工资3倍计算，最高不超过12年
    """
    try:
        result = CompensationCalculator.calculate_illegal_termination(
            entry_date=request.entry_date,
            leave_date=request.leave_date,
            monthly_salary=request.monthly_salary,
            average_salary_12m=request.average_salary_12m,
            city=request.city,
            high_salary_cap=request.high_salary_cap,
            is_negotiated=request.is_negotiated
        )
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


@router.post("/overtime", response_model=ResponseModel)
async def calc_overtime(request: OvertimeCalc):
    """
    加班费计算

    计算标准：
    - 工作日加班：小时工资 × 150%
    - 休息日加班：小时工资 × 200%
    - 法定节假日加班：小时工资 × 300%

    小时工资 = 月工资 ÷ 21.75 ÷ 8
    """
    try:
        result = CompensationCalculator.calculate_overtime(
            monthly_salary=request.monthly_salary,
            workday_hours=request.workday_hours,
            weekend_hours=request.weekend_hours,
            holiday_hours=request.holiday_hours,
            work_days_per_month=request.work_days_per_month
        )
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


@router.post("/annual-leave", response_model=ResponseModel)
async def calc_annual_leave(request: AnnualLeaveCalc):
    """
    未休年休假工资计算

    年休假标准：
    - 累计工作满1年不满10年：5天
    - 累计工作满10年不满20年：10天
    - 累计工作满20年：15天

    未休年休假工资 = 日工资 × 未休天数 × 300%
    日工资 = 月工资 ÷ 21.75
    """
    try:
        result = CompensationCalculator.calculate_annual_leave(
            monthly_salary=request.monthly_salary,
            total_work_years=request.total_work_years,
            unused_days=request.unused_days,
            work_days_per_month=request.work_days_per_month
        )
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


@router.get("/social-average-salary", response_model=ResponseModel)
async def get_social_average_salary():
    """
    获取各城市社会平均工资（参考数据）

    数据来源：2023年各城市公布的社平工资
    """
    return ResponseModel(data=CompensationCalculator.SOCIAL_AVERAGE_SALARY)
