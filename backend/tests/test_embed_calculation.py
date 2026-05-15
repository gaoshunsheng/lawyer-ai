"""Test calculator embedding in documents."""
from app.services.calculator_service import calculate


def test_calculate_illegal_termination_basic():
    result = calculate("illegal_termination", {"monthly_salary": 10000, "work_years": 3})
    assert result.result > 0
    assert result.result == 60000.0  # 2N = 10000 * 3 * 2


def test_calculate_overtime_basic():
    result = calculate("overtime", {
        "monthly_salary": 8000,
        "workday_hours": 10,
        "weekend_hours": 8,
        "holiday_hours": 4,
    })
    assert result.result > 0
    assert len(result.steps) >= 4  # 3 types + total


def test_calculate_annual_leave_basic():
    result = calculate("annual_leave", {
        "monthly_salary": 10000,
        "used_leave_days": 2,
        "work_years_total": 5,
    })
    assert result.result > 0
    assert "5天" in result.steps[0]


def test_calculate_work_injury_basic():
    result = calculate("work_injury", {
        "monthly_salary": 8000,
        "disability_level": 10,
    })
    assert result.result == 8000 * 7  # 10级 = 7个月


def test_calculate_invalid_type():
    import pytest
    with pytest.raises(ValueError, match="不支持的计算类型"):
        calculate("invalid_type", {})


def test_calculate_result_has_all_fields():
    result = calculate("illegal_termination", {"monthly_salary": 5000, "work_years": 1})
    assert hasattr(result, "result")
    assert hasattr(result, "breakdown")
    assert hasattr(result, "basis")
    assert hasattr(result, "steps")
    assert isinstance(result.basis, list)
    assert isinstance(result.steps, list)
    assert isinstance(result.breakdown, dict)


def test_calculate_illegal_termination_high_salary_cap():
    result = calculate("illegal_termination", {
        "monthly_salary": 100000,
        "work_years": 8,
        "city": "北京",
        "is_high_salary": True,
    })
    # Should be capped at 3x social average
    assert result.breakdown["is_capped"] is True
    assert result.result < 100000 * 8 * 2  # Must be less than uncapped


def test_calculate_overtime_zero_hours():
    result = calculate("overtime", {"monthly_salary": 6000})
    assert result.result == 0


def test_calculate_annual_leave_under_one_year():
    result = calculate("annual_leave", {
        "monthly_salary": 8000,
        "work_years_total": 0.5,
    })
    assert result.result == 0
