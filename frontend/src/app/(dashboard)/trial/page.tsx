"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { TRIAL_MODES, TRIAL_ROLES } from "@/lib/constants";
import type { CaseItem, TrialSimulation } from "@/types";

export default function TrialListPage() {
  const { token } = useAuth();
  const router = useRouter();

  const [trials, setTrials] = useState<TrialSimulation[]>([]);
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form state
  const [selectedCaseId, setSelectedCaseId] = useState("");
  const [selectedMode, setSelectedMode] = useState("");
  const [selectedRole, setSelectedRole] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchTrials = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<TrialSimulation[]>("/trial/list", token);
      setTrials(data);
    } catch {
      // handled silently
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchCases = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<{ items: CaseItem[]; total: number }>(
        "/cases?page=1&page_size=100",
        token
      );
      setCases(data.items);
    } catch {
      // handled silently
    }
  }, [token]);

  useEffect(() => {
    fetchTrials();
    fetchCases();
  }, [fetchTrials, fetchCases]);

  const handleCreate = async () => {
    if (!token || !selectedCaseId || !selectedMode || !selectedRole) return;
    setSubmitting(true);
    try {
      await api.post<TrialSimulation>(
        `/cases/${selectedCaseId}/trial/start`,
        { mode: selectedMode, role: selectedRole },
        token
      );
      setShowModal(false);
      setSelectedCaseId("");
      setSelectedMode("");
      setSelectedRole("");
      fetchTrials();
    } catch (err) {
      alert(err instanceof Error ? err.message : "创建失败");
    } finally {
      setSubmitting(false);
    }
  };

  const statusBadge = (status: string) => {
    if (status === "active") {
      return (
        <span className="inline-block rounded-full px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700">
          进行中
        </span>
      );
    }
    if (status === "completed") {
      return (
        <span className="inline-block rounded-full px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700">
          已完成
        </span>
      );
    }
    return (
      <span className="inline-block rounded-full px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700">
        {status}
      </span>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">庭审模拟</h1>
          <p className="text-sm text-muted-foreground mt-1">
            AI 驱动的庭审模拟与策略分析
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
        >
          + 新建模拟
        </button>
      </div>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : trials.length === 0 ? (
        <p className="text-center text-muted-foreground py-8">暂无数据</p>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left font-medium">案件编号</th>
                <th className="px-4 py-3 text-left font-medium">模式</th>
                <th className="px-4 py-3 text-left font-medium">角色</th>
                <th className="px-4 py-3 text-left font-medium">轮次</th>
                <th className="px-4 py-3 text-left font-medium">状态</th>
                <th className="px-4 py-3 text-left font-medium">创建时间</th>
                <th className="px-4 py-3 text-left font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {trials.map((t) => {
                const matchedCase = cases.find((c) => c.id === t.case_id);
                return (
                  <tr key={t.id} className="border-t hover:bg-muted/30">
                    <td className="px-4 py-3 font-mono text-xs">
                      {matchedCase?.case_number || t.case_id.slice(0, 8)}
                    </td>
                    <td className="px-4 py-3">
                      {TRIAL_MODES[t.mode] || t.mode}
                    </td>
                    <td className="px-4 py-3">
                      {TRIAL_ROLES[t.role] || t.role}
                    </td>
                    <td className="px-4 py-3">{t.rounds_completed}</td>
                    <td className="px-4 py-3">{statusBadge(t.status)}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {new Date(t.created_at).toLocaleDateString("zh-CN")}
                    </td>
                    <td className="px-4 py-3">
                      {t.status === "active" ? (
                        <button
                          onClick={() => router.push(`/trial/${t.id}`)}
                          className="rounded-md bg-primary px-3 py-1 text-xs text-primary-foreground hover:bg-primary/90"
                        >
                          继续
                        </button>
                      ) : (
                        <button
                          onClick={() => router.push(`/trial/${t.id}`)}
                          className="rounded-md border px-3 py-1 text-xs hover:bg-accent"
                        >
                          查看报告
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* New Simulation Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-background rounded-lg border shadow-lg w-full max-w-md p-6 space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">新建模拟</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-muted-foreground hover:text-foreground text-xl leading-none"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">选择案件</label>
                <select
                  value={selectedCaseId}
                  onChange={(e) => setSelectedCaseId(e.target.value)}
                  className="w-full rounded-md border px-3 py-2 text-sm bg-background"
                >
                  <option value="">请选择案件</option>
                  {cases.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.case_number} - {c.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">模拟模式</label>
                <select
                  value={selectedMode}
                  onChange={(e) => setSelectedMode(e.target.value)}
                  className="w-full rounded-md border px-3 py-2 text-sm bg-background"
                >
                  <option value="">请选择模式</option>
                  {Object.entries(TRIAL_MODES).map(([k, v]) => (
                    <option key={k} value={k}>
                      {v}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">扮演角色</label>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="w-full rounded-md border px-3 py-2 text-sm bg-background"
                >
                  <option value="">请选择角色</option>
                  {Object.entries(TRIAL_ROLES).map(([k, v]) => (
                    <option key={k} value={k}>
                      {v}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setShowModal(false)}
                className="rounded-md border px-4 py-2 text-sm hover:bg-accent"
              >
                取消
              </button>
              <button
                onClick={handleCreate}
                disabled={
                  !selectedCaseId || !selectedMode || !selectedRole || submitting
                }
                className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {submitting ? "创建中..." : "开始模拟"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
