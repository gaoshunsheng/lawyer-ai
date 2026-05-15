"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { CASE_TYPES, CASE_STATUSES } from "@/lib/constants";
import type { CaseOverview, TrendPeriod, LawyerStat } from "@/types";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  ResponsiveContainer,
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#6366f1"];

type TabKey = "overview" | "trends" | "performance";

export default function ReportsPage() {
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState<TabKey>("overview");

  // Overview state
  const [overview, setOverview] = useState<CaseOverview | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(true);

  // Trends state
  const [trends, setTrends] = useState<TrendPeriod[]>([]);
  const [trendsLoading, setTrendsLoading] = useState(true);

  // Performance state
  const [lawyers, setLawyers] = useState<LawyerStat[]>([]);
  const [perfLoading, setPerfLoading] = useState(true);

  const isAdmin = user?.role === "platform_admin" || user?.role === "tenant_admin";

  // Fetch overview
  const fetchOverview = useCallback(async () => {
    if (!token) return;
    setOverviewLoading(true);
    try {
      const data = await api.get<CaseOverview>("/reports/case-overview?days=90", token);
      setOverview(data);
    } catch {
      // handled silently
    } finally {
      setOverviewLoading(false);
    }
  }, [token]);

  // Fetch trends
  const fetchTrends = useCallback(async () => {
    if (!token) return;
    setTrendsLoading(true);
    try {
      const data = await api.get<{ periods: TrendPeriod[] }>(
        "/reports/trends?granularity=month&days=180",
        token
      );
      setTrends(data.periods);
    } catch {
      // handled silently
    } finally {
      setTrendsLoading(false);
    }
  }, [token]);

  // Fetch lawyer performance
  const fetchPerformance = useCallback(async () => {
    if (!token || !isAdmin) return;
    setPerfLoading(true);
    try {
      const data = await api.get<{ lawyers: LawyerStat[]; period_days: number }>(
        "/reports/lawyer-performance?period_days=90",
        token
      );
      const sorted = [...data.lawyers].sort((a, b) => b.total_cases - a.total_cases);
      setLawyers(sorted);
    } catch {
      // handled silently
    } finally {
      setPerfLoading(false);
    }
  }, [token, isAdmin]);

  useEffect(() => {
    if (activeTab === "overview") fetchOverview();
    else if (activeTab === "trends") fetchTrends();
    else if (activeTab === "performance") fetchPerformance();
  }, [activeTab, fetchOverview, fetchTrends, fetchPerformance]);

  const tabs: { key: TabKey; label: string }[] = [
    { key: "overview", label: "案件概览" },
    { key: "trends", label: "趋势分析" },
    { key: "performance", label: "律师绩效" },
  ];

  // ── Pie chart data for case types ──
  const pieData = (overview?.by_type || []).map((item) => ({
    name: CASE_TYPES[item.type] || item.type,
    value: item.count,
  }));

  // ── Bar chart data for case statuses ──
  const statusData = (overview?.by_status || []).map((item) => ({
    name: CASE_STATUSES[item.status] || item.status,
    count: item.count,
  }));

  // ── Stacked bar chart data for trends by type ──
  const typeKeys = trends.length > 0 ? Object.keys(trends[0].by_type || {}) : [];
  const stackedData = trends.map((period) => ({
    period: period.period,
    total: period.total,
    ...Object.fromEntries(
      typeKeys.map((key) => [CASE_TYPES[key] || key, period.by_type[key] || 0])
    ),
  }));

  // ── Win rate color helper ──
  const winRateColor = (rate: number) => {
    if (rate > 80) return "text-green-600";
    if (rate > 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">数据报表</h1>
        <p className="text-sm text-muted-foreground mt-1">案件数据统计与分析</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`rounded-md px-4 py-2 text-sm ${
              activeTab === tab.key
                ? "bg-primary text-primary-foreground"
                : "border hover:bg-muted/50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Tab 1: 案件概览 ── */}
      {activeTab === "overview" && (
        <>
          {overviewLoading ? (
            <p className="text-center text-muted-foreground py-8">加载中...</p>
          ) : overview ? (
            <>
              {/* Summary cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">案件总数</p>
                  <p className="text-2xl font-bold mt-1">{overview.total}</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">平均周期</p>
                  <p className="text-2xl font-bold mt-1">{overview.avg_duration_days} 天</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">胜诉率</p>
                  <p className="text-2xl font-bold mt-1">{overview.win_rate.toFixed(1)}%</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">总标的额</p>
                  <p className="text-2xl font-bold mt-1">
                    ¥{overview.total_claim_amount.toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Charts side by side */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Pie chart: case type distribution */}
                <div className="rounded-lg border p-5">
                  <h3 className="text-sm font-medium mb-4">案件类型分布</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        dataKey="value"
                        label={({ name, percent }) =>
                          `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                        }
                      >
                        {pieData.map((_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Bar chart: case status distribution */}
                <div className="rounded-lg border p-5">
                  <h3 className="text-sm font-medium mb-4">案件状态分布</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={statusData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          ) : (
            <p className="text-center text-muted-foreground py-8">暂无数据</p>
          )}
        </>
      )}

      {/* ── Tab 2: 趋势分析 ── */}
      {activeTab === "trends" && (
        <>
          {trendsLoading ? (
            <p className="text-center text-muted-foreground py-8">加载中...</p>
          ) : trends.length > 0 ? (
            <>
              {/* Line chart: case count over time */}
              <div className="rounded-lg border p-5">
                <h3 className="text-sm font-medium mb-4">案件数量趋势</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="total"
                      name="案件总数"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Stacked bar chart: by type breakdown */}
              <div className="rounded-lg border p-5">
                <h3 className="text-sm font-medium mb-4">案件类型构成趋势</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={stackedData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {typeKeys.map((key, index) => (
                      <Bar
                        key={key}
                        dataKey={CASE_TYPES[key] || key}
                        stackId="types"
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <p className="text-center text-muted-foreground py-8">暂无趋势数据</p>
          )}
        </>
      )}

      {/* ── Tab 3: 律师绩效 ── */}
      {activeTab === "performance" && (
        <>
          {!isAdmin ? (
            <p className="text-center text-muted-foreground py-8">仅管理员可查看</p>
          ) : perfLoading ? (
            <p className="text-center text-muted-foreground py-8">加载中...</p>
          ) : lawyers.length > 0 ? (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">姓名</th>
                    <th className="px-4 py-3 text-left font-medium">案件数</th>
                    <th className="px-4 py-3 text-left font-medium">胜诉率</th>
                    <th className="px-4 py-3 text-left font-medium">满意度</th>
                    <th className="px-4 py-3 text-left font-medium">标的总额</th>
                  </tr>
                </thead>
                <tbody>
                  {lawyers.map((l) => (
                    <tr key={l.user_id} className="border-t hover:bg-muted/30">
                      <td className="px-4 py-3 font-medium">{l.name}</td>
                      <td className="px-4 py-3">{l.total_cases}</td>
                      <td className="px-4 py-3">
                        <span className={winRateColor(l.win_rate)}>
                          {l.win_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-4 py-3">{l.avg_satisfaction.toFixed(1)}</td>
                      <td className="px-4 py-3">
                        ¥{l.total_claim_amount.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">暂无绩效数据</p>
          )}
        </>
      )}
    </div>
  );
}
