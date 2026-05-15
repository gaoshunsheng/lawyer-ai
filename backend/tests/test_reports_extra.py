"""Extra tests for reports — schemas, edge cases, service functions."""

import pytest

from app.schemas.report import (
    CaseOverviewResponse,
    CaseTypeStat,
    CaseStatusStat,
    TrendsResponse,
    TrendPeriod,
    LawyerPerformanceResponse,
    LawyerStat,
    ClientReportResponse,
    ClientCaseSummary,
)


# ── CaseOverviewResponse edge cases ──


def test_case_overview_zero_total():
    resp = CaseOverviewResponse(
        total=0, by_type=[], by_status=[],
        avg_duration_days=0.0, win_rate=0.0, total_claim_amount=0.0,
    )
    assert resp.total == 0
    assert resp.win_rate == 0.0


def test_case_overview_large_numbers():
    resp = CaseOverviewResponse(
        total=99999, by_type=[], by_status=[],
        avg_duration_days=365.5, win_rate=99.9, total_claim_amount=999999999.99,
    )
    assert resp.total == 99999
    assert resp.total_claim_amount == 999999999.99


def test_case_overview_with_multiple_types():
    resp = CaseOverviewResponse(
        total=100,
        by_type=[
            CaseTypeStat(type="labor_contract", count=40, amount=2000000),
            CaseTypeStat(type="tort", count=30, amount=3000000),
            CaseTypeStat(type="ip_dispute", count=30, amount=5000000),
        ],
        by_status=[],
        avg_duration_days=45.0, win_rate=65.0, total_claim_amount=10000000,
    )
    assert len(resp.by_type) == 3
    assert resp.by_type[2].type == "ip_dispute"


def test_case_overview_with_multiple_statuses():
    resp = CaseOverviewResponse(
        total=80,
        by_type=[],
        by_status=[
            CaseStatusStat(status="active", count=30),
            CaseStatusStat(status="closed", count=40),
            CaseStatusStat(status="archived", count=10),
        ],
        avg_duration_days=30.0, win_rate=50.0, total_claim_amount=5000000,
    )
    assert len(resp.by_status) == 3
    assert resp.by_status[0].count == 30


# ── TrendPeriod and TrendsResponse ──


def test_trend_period_with_empty_by_type():
    period = TrendPeriod(period="2026-03", total=0, by_type={}, avg_amount=0.0)
    assert period.by_type == {}


def test_trends_response_multiple_periods():
    resp = TrendsResponse(periods=[
        TrendPeriod(period="2026-01", total=10, by_type={"labor_contract": 5}, avg_amount=50000),
        TrendPeriod(period="2026-02", total=15, by_type={"labor_contract": 8, "tort": 7}, avg_amount=60000),
        TrendPeriod(period="2026-03", total=12, by_type={"labor_contract": 6}, avg_amount=55000),
    ])
    assert len(resp.periods) == 3
    assert resp.periods[1].by_type["tort"] == 7


def test_trend_period_various_case_types():
    period = TrendPeriod(
        period="2026-04",
        total=50,
        by_type={"labor_contract": 20, "tort": 15, "ip_dispute": 10, "contract_dispute": 5},
        avg_amount=75000.5,
    )
    assert len(period.by_type) == 4
    assert period.avg_amount == 75000.5


# ── LawyerStat edge cases ──


def test_lawyer_stat_zero_cases():
    stat = LawyerStat(
        user_id="uuid-0", name="新律师", total_cases=0,
        win_rate=0.0, avg_satisfaction=0.0, total_claim_amount=0.0,
    )
    assert stat.total_cases == 0
    assert stat.win_rate == 0.0


def test_lawyer_stat_100_percent_win_rate():
    stat = LawyerStat(
        user_id="uuid-1", name="王牌律师", total_cases=50,
        win_rate=1.0, avg_satisfaction=5.0, total_claim_amount=10000000,
    )
    assert stat.win_rate == 1.0


def test_lawyer_stat_fractional_values():
    stat = LawyerStat(
        user_id="uuid-2", name="普通律师", total_cases=13,
        win_rate=0.615, avg_satisfaction=3.7, total_claim_amount=123456.78,
    )
    assert stat.win_rate == 0.615
    assert stat.avg_satisfaction == 3.7


# ── LawyerPerformanceResponse ──


def test_lawyer_performance_empty():
    resp = LawyerPerformanceResponse(lawyers=[], period_days=30)
    assert resp.lawyers == []
    assert resp.period_days == 30


def test_lawyer_performance_multiple_lawyers():
    resp = LawyerPerformanceResponse(
        lawyers=[
            LawyerStat(user_id="u1", name="张律师", total_cases=10, win_rate=0.8, avg_satisfaction=4.2, total_claim_amount=500000),
            LawyerStat(user_id="u2", name="李律师", total_cases=8, win_rate=0.75, avg_satisfaction=4.0, total_claim_amount=400000),
        ],
        period_days=90,
    )
    assert len(resp.lawyers) == 2
    assert resp.lawyers[0].name == "张律师"


def test_lawyer_performance_period_variants():
    for days in (7, 30, 90, 180, 365):
        resp = LawyerPerformanceResponse(lawyers=[], period_days=days)
        assert resp.period_days == days


# ── ClientReportResponse and ClientCaseSummary ──


def test_client_case_summary():
    summary = ClientCaseSummary(
        id="case-1", title="劳动争议案", status="active",
        claim_amount=50000.0, created_at="2026-01-15",
    )
    assert summary.id == "case-1"
    assert summary.claim_amount == 50000.0


def test_client_case_summary_no_amount():
    summary = ClientCaseSummary(
        id="case-2", title="合同纠纷", status="closed",
        claim_amount=None, created_at="2026-02-20",
    )
    assert summary.claim_amount is None


def test_client_report_response():
    resp = ClientReportResponse(
        client_name="张三",
        summary={"total_cases": 3, "total_amount": 150000},
        cases=[
            ClientCaseSummary(id="c1", title="案件A", status="active", claim_amount=50000, created_at="2026-01-01"),
        ],
    )
    assert resp.client_name == "张三"
    assert resp.summary["total_cases"] == 3
    assert len(resp.cases) == 1


# ── Report service functions exist ──


def test_report_service_functions_callable():
    from app.services.report_service import (
        get_case_overview,
        get_trends,
        get_lawyer_performance,
    )
    for fn in [get_case_overview, get_trends, get_lawyer_performance]:
        assert callable(fn)
