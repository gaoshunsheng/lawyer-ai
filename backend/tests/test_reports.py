import pytest
from app.schemas.report import (
    CaseOverviewResponse,
    CaseTypeStat,
    CaseStatusStat,
    TrendsResponse,
    TrendPeriod,
    LawyerPerformanceResponse,
    LawyerStat,
)


def test_case_overview_schema():
    resp = CaseOverviewResponse(
        total=120, by_type=[], by_status=[],
        avg_duration_days=45.2, win_rate=72.5, total_claim_amount=8500000,
    )
    assert resp.total == 120
    assert resp.win_rate == 72.5


def test_case_type_stat():
    stat = CaseTypeStat(type="labor_contract", count=45, amount=2300000)
    assert stat.type == "labor_contract"
    assert stat.count == 45


def test_case_status_stat():
    stat = CaseStatusStat(status="active", count=30)
    assert stat.status == "active"


def test_trends_response():
    resp = TrendsResponse(periods=[
        TrendPeriod(period="2026-01", total=12, by_type={"labor_contract": 5}, avg_amount=50000),
    ])
    assert resp.periods[0].total == 12
    assert resp.periods[0].by_type["labor_contract"] == 5


def test_trends_response_empty():
    resp = TrendsResponse(periods=[])
    assert resp.periods == []


def test_lawyer_stat():
    stat = LawyerStat(
        user_id="uuid-1", name="张律师", total_cases=25,
        win_rate=0.85, avg_satisfaction=4.5, total_claim_amount=1500000,
    )
    assert stat.total_cases == 25


def test_lawyer_performance():
    resp = LawyerPerformanceResponse(
        lawyers=[LawyerStat(
            user_id="uuid-1", name="张律师", total_cases=10,
            win_rate=0.8, avg_satisfaction=4.2, total_claim_amount=500000,
        )],
        period_days=90,
    )
    assert resp.period_days == 90
    assert len(resp.lawyers) == 1


def test_overview_with_data():
    resp = CaseOverviewResponse(
        total=50,
        by_type=[CaseTypeStat(type="labor_contract", count=20, amount=1000000)],
        by_status=[CaseStatusStat(status="active", count=15)],
        avg_duration_days=30.0, win_rate=60.0, total_claim_amount=2000000,
    )
    assert resp.by_type[0].count == 20
    assert resp.by_status[0].count == 15
