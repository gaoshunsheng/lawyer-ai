"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";

interface FeedbackStats {
  total: number;
  positive_rate: number;
  negative_rate: number;
  avg_law_accuracy: number;
  avg_analysis_depth: number;
  avg_practical_value: number;
}

interface TrendPoint {
  period: string;
  total: number;
  positive: number;
  negative: number;
  satisfaction_rate: number;
}

export default function FeedbackPage() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [granularity, setGranularity] = useState("day");

  const isAdmin = user?.role === "platform_admin" || user?.role === "tenant_admin";

  const fetchData = useCallback(async () => {
    if (!token || !isAdmin) return;
    setLoading(true);
    try {
      const [statsRes, trendsRes] = await Promise.all([
        api.get<FeedbackStats>(`/feedback/stats?days=${days}`, token),
        api.get<TrendPoint[]>(`/feedback/trends?days=${days}&granularity=${granularity}`, token),
      ]);
      setStats(statsRes);
      setTrends(trendsRes);
    } finally {
      setLoading(false);
    }
  }, [token, isAdmin, days, granularity]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (!isAdmin) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold">反馈看板</h1>
        <p className="text-muted-foreground mt-4">仅管理员可查看反馈统计数据。</p>
      </div>
    );
  }

  // Simple bar chart using CSS (no external chart library needed)
  const maxSatisfaction = Math.max(...trends.map((t) => t.satisfaction_rate), 1);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">反馈看板</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {days === 1 ? "今日" : days === 7 ? "本周" : days === 30 ? "本月" : `近${days}天`}数据
          </p>
        </div>
        <div className="flex gap-2">
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}
            className="rounded-md border px-3 py-2 text-sm bg-background">
            <option value={1}>今日</option>
            <option value={7}>近7天</option>
            <option value={30}>近30天</option>
            <option value={90}>近90天</option>
          </select>
          <select value={granularity} onChange={(e) => setGranularity(e.target.value)}
            className="rounded-md border px-3 py-2 text-sm bg-background">
            <option value="day">按日</option>
            <option value="week">按周</option>
            <option value="month">按月</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">总评价数</p>
              <p className="text-2xl font-bold mt-1">{stats?.total || 0}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">好评率</p>
              <p className={`text-2xl font-bold mt-1 ${(stats?.positive_rate || 0) >= 85 ? "text-green-600" : "text-yellow-600"}`}>
                {stats?.positive_rate || 0}%
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">差评率</p>
              <p className={`text-2xl font-bold mt-1 ${(stats?.negative_rate || 0) > 15 ? "text-red-600" : "text-green-600"}`}>
                {stats?.negative_rate || 0}%
                {(stats?.negative_rate || 0) > 15 && (
                  <span className="text-xs font-normal text-red-500 ml-2">⚠ 预警</span>
                )}
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">综合均分</p>
              <p className="text-2xl font-bold mt-1">
                {stats ? ((stats.avg_law_accuracy + stats.avg_analysis_depth + stats.avg_practical_value) / 3).toFixed(1) : "-"}
              </p>
            </div>
          </div>

          {/* Dimension scores */}
          {stats && (
            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm text-muted-foreground">法条准确性</p>
                <p className="text-xl font-bold mt-1">{stats.avg_law_accuracy.toFixed(1)}</p>
                <div className="flex justify-center gap-0.5 mt-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <span key={s} className={`text-sm ${s <= Math.round(stats.avg_law_accuracy) ? "text-yellow-400" : "text-gray-300"}`}>★</span>
                  ))}
                </div>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm text-muted-foreground">分析深度</p>
                <p className="text-xl font-bold mt-1">{stats.avg_analysis_depth.toFixed(1)}</p>
                <div className="flex justify-center gap-0.5 mt-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <span key={s} className={`text-sm ${s <= Math.round(stats.avg_analysis_depth) ? "text-yellow-400" : "text-gray-300"}`}>★</span>
                  ))}
                </div>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm text-muted-foreground">实用价值</p>
                <p className="text-xl font-bold mt-1">{stats.avg_practical_value.toFixed(1)}</p>
                <div className="flex justify-center gap-0.5 mt-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <span key={s} className={`text-sm ${s <= Math.round(stats.avg_practical_value) ? "text-yellow-400" : "text-gray-300"}`}>★</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Satisfaction trends */}
          <div className="rounded-lg border p-5">
            <h2 className="text-lg font-semibold mb-4">满意度趋势</h2>
            {trends.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">暂无趋势数据</p>
            ) : (
              <div className="space-y-2">
                {trends.map((t) => (
                  <div key={t.period} className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground w-24 shrink-0">
                      {granularity === "month"
                        ? t.period.slice(0, 7)
                        : t.period.slice(0, 10)}
                    </span>
                    <div className="flex-1 bg-muted rounded-full h-6 relative overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${t.satisfaction_rate >= 85 ? "bg-green-500" : t.satisfaction_rate >= 70 ? "bg-yellow-500" : "bg-red-500"}`}
                        style={{ width: `${Math.max(t.satisfaction_rate, 2)}%` }}
                      />
                    </div>
                    <span className={`text-xs font-medium w-14 text-right ${t.satisfaction_rate >= 85 ? "text-green-600" : t.satisfaction_rate >= 70 ? "text-yellow-600" : "text-red-600"}`}>
                      {t.satisfaction_rate}%
                    </span>
                    <span className="text-xs text-muted-foreground w-16 text-right">
                      {t.total}条
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Alert section */}
          {(stats?.negative_rate || 0) > 15 && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4">
              <h3 className="font-semibold text-red-700 flex items-center gap-2">
                <span>⚠</span> 差评率预警
              </h3>
              <p className="text-sm text-red-600 mt-1">
                当前差评率为 {stats?.negative_rate}%，超过15%阈值。建议检查近期的AI回复质量，并查看具体差评内容以定位问题。
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
