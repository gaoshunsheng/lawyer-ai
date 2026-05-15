import pytest
from app.services.calculator_service import calculate


def test_illegal_termination_basic():
    result = calculate("illegal_termination", {"monthly_salary": 10000, "work_years": 3})
    assert result.result == 60000  # 10000 * 3 * 2
    assert "劳动合同法" in result.basis[0]


def test_illegal_termination_half_year():
    result = calculate("illegal_termination", {"monthly_salary": 10000, "work_years": 0.5})
    assert result.result == 20000  # 0.5年按N=1算 → 10000 * 1 * 2


def test_illegal_termination_high_salary_cap():
    result = calculate("illegal_termination", {"monthly_salary": 50000, "work_years": 5, "city": "北京"})
    social_avg = 13930
    cap = social_avg * 3
    expected = cap * 5 * 2
    assert result.result == round(expected, 2)


def test_overtime_workday():
    result = calculate("overtime", {"monthly_salary": 8700, "workday_hours": 10})
    hourly = 8700 / 21.75 / 8
    expected = hourly * 1.5 * 10
    assert abs(result.result - round(expected, 2)) < 0.01


def test_overtime_all_types():
    result = calculate("overtime", {
        "monthly_salary": 8700,
        "workday_hours": 10,
        "weekend_hours": 8,
        "holiday_hours": 8,
    })
    hourly = 8700 / 21.75 / 8
    expected = hourly * 1.5 * 10 + hourly * 2.0 * 8 + hourly * 3.0 * 8
    assert abs(result.result - round(expected, 2)) < 0.01


def test_annual_leave():
    result = calculate("annual_leave", {
        "monthly_salary": 8700,
        "total_leave_days": 5,
        "used_leave_days": 2,
        "work_years_total": 5,
    })
    daily = 8700 / 21.75
    expected = daily * 2 * 3  # 200% * 3天未休
    assert abs(result.result - round(expected, 2)) < 0.01


def test_annual_leave_less_than_one_year():
    result = calculate("annual_leave", {
        "monthly_salary": 8700,
        "total_leave_days": 5,
        "used_leave_days": 0,
        "work_years_total": 0.5,
    })
    assert result.result == 0


def test_work_injury_level_10():
    result = calculate("work_injury", {
        "monthly_salary": 8000,
        "disability_level": 10,
        "is_resign": True,
        "city": "北京",
    })
    # 一次性伤残补助金: 7个月 × 8000 = 56000
    # 一次性工伤医疗补助金: 13930 × 20 = 278600
    # 一次性伤残就业补助金: 13930 × 15 = 208950
    assert result.result > 56000


def test_work_injury_level_1():
    result = calculate("work_injury", {
        "monthly_salary": 8000,
        "disability_level": 1,
        "city": "全国",
    })
    assert result.result == 8000 * 27  # 216000
    assert result.breakdown["monthly_disability_allowance"]["monthly_amount"] == 8000 * 0.9


def test_invalid_calc_type():
    with pytest.raises(ValueError, match="不支持的计算类型"):
        calculate("invalid_type", {})
