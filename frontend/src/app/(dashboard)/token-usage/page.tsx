"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api-client";
import { useAuth } from "@/providers/auth-provider";

interface BudgetStatus {
  entity_type: string;
  entity_id: string;
  budget: number | null;
  used: number;
  remaining: number | null;
  percentage: number | null;
}

interface DailyUsage {
  date: string;
  model_name: string;
  agent_type: string | null;
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  total_cost_cny: number | null;
  request_count: number;
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

function formatCNY(n: number | null): string {
  if (n == null) return "-";
  return `¥${n.toFixed(4)}`;
}

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

function getDaysAgo(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

export default function TokenUsagePage() {
  const { token } = useAuth();
  const [budgets, setBudgets] = useState<BudgetStatus[]>([]);
  const [daily, setDaily] = useState<DailyUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState(getDaysAgo(30));
  const [endDate, setEndDate] = useState(getToday());

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [budgetData, dailyData] = await Promise.all([
        api.get<BudgetStatus[]>("/token-usage/budget", token),
        api.get<DailyUsage[]>(
          `/token-usage/daily?start_date=${startDate}&end_date=${endDate}`,
          token
        ),
      ]);
      setBudgets(budgetData);
      setDaily(dailyData);
    } catch (err) {
      console.error("获取 Token 用量失败:", err);
    } finally {
      setLoading(false);
    }
  }, [token, startDate, endDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const totalTokens = daily.reduce((sum, d) => sum + d.total_tokens, 0);
  const totalCost = daily.reduce((sum, d) => sum + (d.total_cost_cny || 0), 0);
  const totalRequests = daily.reduce((sum, d) => sum + d.request_count, 0);

  const entityLabel: Record<string, string> = {
    user: "个人",
    department: "部门",
    tenant: "租户",
  };

  if (loading) {
    return <div className="p-6 text-muted-foreground">加载中...</div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-6xl">
      <h1 className="text-2xl font-bold">Token 用量监控</h1>

      {/* 预算状态 */}
      {budgets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {budgets.map((b) => (
            <div key={b.entity_type} className="rounded-lg border p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{entityLabel[b.entity_type] || b.entity_type} 预算</span>
                <span className="text-xs text-muted-foreground">
                  {b.budget ? formatTokens(b.budget) : "无限制"}
                </span>
              </div>
              {b.budget && b.percentage != null && (
                <div className="space-y-1">
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        b.percentage > 80 ? "bg-destructive" : b.percentage > 50 ? "bg-yellow-500" : "bg-primary"
                      }`}
                      style={{ width: `${Math.min(b.percentage, 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>已用 {formatTokens(b.used)}</span>
                    <span>剩余 {b.remaining != null ? formatTokens(b.remaining) : "-"}</span>
                  </div>
                  <p className="text-xs text-right">{b.percentage}%</p>
                </div>
              )}
              {!b.budget && (
                <p className="text-xs text-muted-foreground">已用 {formatTokens(b.used)}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {budgets.length === 0 && (
        <div className="rounded-lg border p-4 text-sm text-muted-foreground">
          暂未配置 Token 预算
        </div>
      )}

      {/* 汇总统计 */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">总 Token 消耗</p>
          <p className="text-2xl font-bold mt-1">{formatTokens(totalTokens)}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">总费用</p>
          <p className="text-2xl font-bold mt-1">{formatCNY(totalCost)}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">请求次数</p>
          <p className="text-2xl font-bold mt-1">{totalRequests}</p>
        </div>
      </div>

      {/* 日期筛选 */}
      <div className="flex items-center gap-3">
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="rounded-md border px-3 py-1.5 text-sm"
        />
        <span className="text-sm text-muted-foreground">至</span>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="rounded-md border px-3 py-1.5 text-sm"
        />
      </div>

      {/* 每日明细 */}
      <div className="rounded-lg border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left px-4 py-3 font-medium">日期</th>
              <th className="text-left px-4 py-3 font-medium">模型</th>
              <th className="text-right px-4 py-3 font-medium">输入 Token</th>
              <th className="text-right px-4 py-3 font-medium">输出 Token</th>
              <th className="text-right px-4 py-3 font-medium">总 Token</th>
              <th className="text-right px-4 py-3 font-medium">费用</th>
              <th className="text-right px-4 py-3 font-medium">请求数</th>
            </tr>
          </thead>
          <tbody>
            {daily.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                  暂无数据
                </td>
              </tr>
            )}
            {daily.map((row, i) => (
              <tr key={i} className="border-t hover:bg-muted/30">
                <td className="px-4 py-2">{row.date}</td>
                <td className="px-4 py-2">{row.model_name}</td>
                <td className="px-4 py-2 text-right">{formatTokens(row.total_input_tokens)}</td>
                <td className="px-4 py-2 text-right">{formatTokens(row.total_output_tokens)}</td>
                <td className="px-4 py-2 text-right font-medium">{formatTokens(row.total_tokens)}</td>
                <td className="px-4 py-2 text-right">{formatCNY(row.total_cost_cny)}</td>
                <td className="px-4 py-2 text-right">{row.request_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
