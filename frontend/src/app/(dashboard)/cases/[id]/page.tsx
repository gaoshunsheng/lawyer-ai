"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { CASE_TYPES, CASE_STATUSES, EVIDENCE_TYPES } from "@/lib/constants";
import type { CaseItem, EvidenceItem, TimelineItem } from "@/types";

const TABS = ["信息", "时间线", "证据", "AI分析"] as const;
type Tab = (typeof TABS)[number];

function AnalysisDisplay({ data }: { data: Record<string, unknown> }) {
  const strengths = (data.strengths as string[]) || [];
  const weaknesses = (data.weaknesses as string[]) || [];
  const risks = (data.risks as { level: string; description: string }[]) || [];
  const strategy = (data.strategy as string[]) || [];
  const winPrediction = data.win_prediction as { probability: number; reasoning: string } | undefined;
  const relevantLaws = (data.relevant_laws as { title: string; article: string; relevance: string }[]) || [];
  const relevantCases = (data.relevant_cases as { name: string; similarity: string; outcome: string }[]) || [];

  const riskBadgeColor = (level: string) => {
    switch (level) {
      case "high": return "bg-red-100 text-red-700";
      case "medium": return "bg-yellow-100 text-yellow-700";
      case "low": return "bg-blue-100 text-blue-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="space-y-4">
      {/* Win Prediction */}
      {winPrediction && (
        <div className="rounded-lg border p-5 bg-primary/5">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">胜诉预测</h3>
            <span className={`text-2xl font-bold ${winPrediction.probability >= 70 ? "text-green-600" : winPrediction.probability >= 40 ? "text-yellow-600" : "text-red-600"}`}>
              {winPrediction.probability}%
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">{winPrediction.reasoning}</p>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-2 gap-4">
        {strengths.length > 0 && (
          <div className="rounded-lg border p-5">
            <h3 className="font-semibold mb-3 text-green-700">优势分析</h3>
            <ul className="space-y-2">
              {strengths.map((s, i) => (
                <li key={i} className="text-sm flex gap-2">
                  <span className="text-green-600 shrink-0">+</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {weaknesses.length > 0 && (
          <div className="rounded-lg border p-5">
            <h3 className="font-semibold mb-3 text-red-700">劣势分析</h3>
            <ul className="space-y-2">
              {weaknesses.map((w, i) => (
                <li key={i} className="text-sm flex gap-2">
                  <span className="text-red-600 shrink-0">-</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Risks */}
      {risks.length > 0 && (
        <div className="rounded-lg border p-5">
          <h3 className="font-semibold mb-3">风险评估（{risks.length}项）</h3>
          <div className="space-y-3">
            {risks.map((r, i) => (
              <div key={i} className="flex gap-3 border-b pb-3 last:border-0">
                <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${riskBadgeColor(r.level)}`}>
                  {r.level === "high" ? "高风险" : r.level === "medium" ? "中风险" : "低风险"}
                </span>
                <p className="text-sm">{r.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strategy */}
      {strategy.length > 0 && (
        <div className="rounded-lg border p-5">
          <h3 className="font-semibold mb-3">策略建议</h3>
          <ul className="space-y-2">
            {strategy.map((s, i) => (
              <li key={i} className="text-sm flex gap-2">
                <span className="text-primary shrink-0">→</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Relevant Laws */}
      {relevantLaws.length > 0 && (
        <div className="rounded-lg border p-5">
          <h3 className="font-semibold mb-3">相关法条</h3>
          <div className="space-y-3">
            {relevantLaws.map((l, i) => (
              <div key={i} className="border-b pb-3 last:border-0">
                <p className="text-sm font-medium">{l.title} - {l.article}</p>
                <p className="text-xs text-muted-foreground mt-1">{l.relevance}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Relevant Cases */}
      {relevantCases.length > 0 && (
        <div className="rounded-lg border p-5">
          <h3 className="font-semibold mb-3">相关判例</h3>
          <div className="space-y-3">
            {relevantCases.map((c, i) => (
              <div key={i} className="border-b pb-3 last:border-0">
                <p className="text-sm font-medium">{c.name}</p>
                <div className="flex gap-4 mt-1">
                  <span className="text-xs text-muted-foreground">相似度：{c.similarity}</span>
                  <span className="text-xs text-muted-foreground">结果：{c.outcome}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const router = useRouter();
  const [caseData, setCaseData] = useState<CaseItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("信息");

  const [evidences, setEvidences] = useState<EvidenceItem[]>([]);
  const [evLoading, setEvLoading] = useState(false);
  const [showEvidenceForm, setShowEvidenceForm] = useState(false);
  const [evTitle, setEvTitle] = useState("");
  const [evType, setEvType] = useState("document");
  const [evDesc, setEvDesc] = useState("");

  const [timelines, setTimelines] = useState<TimelineItem[]>([]);
  const [tlLoading, setTlLoading] = useState(false);
  const [showTimelineForm, setShowTimelineForm] = useState(false);
  const [tlType, setTlType] = useState("milestone");
  const [tlTitle, setTlTitle] = useState("");
  const [tlDesc, setTlDesc] = useState("");
  const [tlDate, setTlDate] = useState("");

  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<Record<string, unknown> | null>(null);

  const fetchCase = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<CaseItem>(`/cases/${id}`, token);
      setCaseData(data);
    } catch {
      router.push("/cases");
    } finally {
      setLoading(false);
    }
  }, [token, id, router]);

  const fetchEvidences = useCallback(async () => {
    if (!token) return;
    setEvLoading(true);
    try {
      const data = await api.get<EvidenceItem[]>(`/cases/${id}/evidences`, token);
      setEvidences(data);
    } finally {
      setEvLoading(false);
    }
  }, [token, id]);

  const fetchTimelines = useCallback(async () => {
    if (!token) return;
    setTlLoading(true);
    try {
      const data = await api.get<TimelineItem[]>(`/cases/${id}/timeline`, token);
      setTimelines(data);
    } finally {
      setTlLoading(false);
    }
  }, [token, id]);

  useEffect(() => { fetchCase(); }, [fetchCase]);
  useEffect(() => { if (tab === "证据") fetchEvidences(); }, [tab, fetchEvidences]);
  useEffect(() => { if (tab === "时间线") fetchTimelines(); }, [tab, fetchTimelines]);

  const addEvidence = async () => {
    if (!token || !evTitle.trim()) return;
    try {
      const params = new URLSearchParams();
      params.set("title", evTitle);
      params.set("evidence_type", evType);
      if (evDesc) params.set("description", evDesc);
      const data = await api.post<EvidenceItem>(`/cases/${id}/evidences?${params.toString()}`, {}, token);
      setEvidences((prev) => [...prev, data]);
      setShowEvidenceForm(false);
      setEvTitle("");
      setEvDesc("");
    } catch {}
  };

  const deleteEvidence = async (eid: string) => {
    if (!token) return;
    try {
      await api.delete(`/cases/${id}/evidences/${eid}`, token);
      setEvidences((prev) => prev.filter((e) => e.id !== eid));
    } catch {}
  };

  const addTimeline = async () => {
    if (!token || !tlTitle.trim() || !tlDate) return;
    try {
      const data = await api.post<TimelineItem>(`/cases/${id}/timeline`, {
        event_type: tlType, title: tlTitle, description: tlDesc || null, event_date: tlDate,
      }, token);
      setTimelines((prev) => [...prev, data]);
      setShowTimelineForm(false);
      setTlTitle("");
      setTlDesc("");
      setTlDate("");
    } catch {}
  };

  const deleteTimeline = async (tid: string) => {
    if (!token) return;
    try {
      await api.delete(`/cases/${id}/timeline/${tid}`, token);
      setTimelines((prev) => prev.filter((t) => t.id !== tid));
    } catch {}
  };

  const fetchAnalysis = async () => {
    if (!token || aiLoading) return;
    setAiLoading(true);
    try {
      const data = await api.post<{ analysis: Record<string, unknown> }>(`/cases/${id}/analyze`, {}, token);
      setAiResult(data.analysis);
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) return <p className="p-6 text-center text-muted-foreground">加载中...</p>;
  if (!caseData) return <p className="p-6 text-center text-muted-foreground">案件不存在</p>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => router.push("/cases")} className="text-sm text-muted-foreground hover:text-foreground mb-1">
            ← 返回案件列表
          </button>
          <h1 className="text-2xl font-bold">{caseData.title}</h1>
          <p className="text-sm text-muted-foreground font-mono">{caseData.case_number}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${
          caseData.status === "closed" || caseData.status === "archived"
            ? "bg-green-100 text-green-700"
            : caseData.status === "cancelled"
            ? "bg-red-100 text-red-700"
            : "bg-blue-100 text-blue-700"
        }`}>
          {CASE_STATUSES[caseData.status] || caseData.status}
        </span>
      </div>

      <div className="flex gap-1 border-b">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "信息" && (
        <div className="grid grid-cols-2 gap-6">
          <div className="rounded-lg border p-5 space-y-3">
            <h2 className="text-lg font-semibold">基本信息</h2>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-muted-foreground">案件类型：</span>{CASE_TYPES[caseData.case_type] || caseData.case_type}</div>
              <div><span className="text-muted-foreground">标的金额：</span>{caseData.claim_amount != null ? `¥${caseData.claim_amount.toLocaleString()}` : "未填写"}</div>
              <div><span className="text-muted-foreground">承办律师：</span>{caseData.lawyer_id}</div>
              <div><span className="text-muted-foreground">律师助理：</span>{caseData.assistant_id || "未指定"}</div>
              <div><span className="text-muted-foreground">创建时间：</span>{new Date(caseData.created_at).toLocaleString("zh-CN")}</div>
              <div><span className="text-muted-foreground">更新时间：</span>{new Date(caseData.updated_at).toLocaleString("zh-CN")}</div>
            </div>
            {caseData.dispute_focus && caseData.dispute_focus.length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">争议焦点</p>
                <div className="flex flex-wrap gap-2">
                  {caseData.dispute_focus.map((d, i) => (
                    <span key={i} className="rounded-full bg-accent px-2.5 py-0.5 text-xs">{d}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="rounded-lg border p-5">
              <h2 className="text-lg font-semibold mb-3">原告信息</h2>
              <div className="space-y-1 text-sm">
                <p><span className="text-muted-foreground">姓名：</span>{caseData.plaintiff?.name || "-"}</p>
                <p><span className="text-muted-foreground">身份证号：</span>{caseData.plaintiff?.id_number || "-"}</p>
                <p><span className="text-muted-foreground">联系方式：</span>{caseData.plaintiff?.contact || "-"}</p>
              </div>
            </div>
            <div className="rounded-lg border p-5">
              <h2 className="text-lg font-semibold mb-3">被告信息</h2>
              <div className="space-y-1 text-sm">
                <p><span className="text-muted-foreground">名称：</span>{caseData.defendant?.name || "-"}</p>
                <p><span className="text-muted-foreground">统一社会信用代码：</span>{caseData.defendant?.id_number || "-"}</p>
                <p><span className="text-muted-foreground">联系方式：</span>{caseData.defendant?.contact || "-"}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {tab === "时间线" && (
        <div className="space-y-4">
          <button
            onClick={() => setShowTimelineForm(!showTimelineForm)}
            className="text-sm rounded-md bg-primary px-3 py-1.5 text-primary-foreground hover:bg-primary/90"
          >
            + 添加事件
          </button>

          {showTimelineForm && (
            <div className="rounded-lg border p-4 space-y-3">
              <div className="flex gap-3">
                <select value={tlType} onChange={(e) => setTlType(e.target.value)} className="rounded-md border px-3 py-2 text-sm bg-background">
                  <option value="milestone">里程碑</option>
                  <option value="task">任务</option>
                  <option value="deadline">截止日期</option>
                  <option value="note">备注</option>
                </select>
                <input type="date" value={tlDate} onChange={(e) => setTlDate(e.target.value)} className="rounded-md border px-3 py-2 text-sm bg-background" />
              </div>
              <input type="text" placeholder="事件标题" value={tlTitle} onChange={(e) => setTlTitle(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <textarea placeholder="事件描述（可选）" value={tlDesc} onChange={(e) => setTlDesc(e.target.value)} rows={2} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <button onClick={addTimeline} disabled={!tlTitle.trim() || !tlDate} className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                保存
              </button>
            </div>
          )}

          {tlLoading ? (
            <p className="text-center text-muted-foreground py-4">加载中...</p>
          ) : timelines.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">暂无时间线事件</p>
          ) : (
            <div className="space-y-3">
              {timelines.map((t) => (
                <div key={t.id} className="flex gap-4 rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground whitespace-nowrap pt-0.5">
                    {new Date(t.event_date).toLocaleDateString("zh-CN")}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`inline-block rounded px-1.5 py-0.5 text-xs font-medium ${
                        t.event_type === "milestone" ? "bg-purple-100 text-purple-700" :
                        t.event_type === "deadline" ? "bg-red-100 text-red-700" :
                        "bg-blue-100 text-blue-700"
                      }`}>
                        {t.event_type === "milestone" ? "里程碑" : t.event_type === "task" ? "任务" : t.event_type === "deadline" ? "截止" : "备注"}
                      </span>
                      <span className="font-medium text-sm">{t.title}</span>
                    </div>
                    {t.description && <p className="text-sm text-muted-foreground mt-1">{t.description}</p>}
                  </div>
                  <button onClick={() => deleteTimeline(t.id)} className="text-sm text-destructive hover:underline shrink-0">
                    删除
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "证据" && (
        <div className="space-y-4">
          <button
            onClick={() => setShowEvidenceForm(!showEvidenceForm)}
            className="text-sm rounded-md bg-primary px-3 py-1.5 text-primary-foreground hover:bg-primary/90"
          >
            + 添加证据
          </button>

          {showEvidenceForm && (
            <div className="rounded-lg border p-4 space-y-3">
              <input type="text" placeholder="证据名称" value={evTitle} onChange={(e) => setEvTitle(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <div className="flex gap-3">
                <select value={evType} onChange={(e) => setEvType(e.target.value)} className="rounded-md border px-3 py-2 text-sm bg-background">
                  {Object.entries(EVIDENCE_TYPES).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
              <textarea placeholder="证据说明（可选）" value={evDesc} onChange={(e) => setEvDesc(e.target.value)} rows={2} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <button onClick={addEvidence} disabled={!evTitle.trim()} className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                保存
              </button>
            </div>
          )}

          {evLoading ? (
            <p className="text-center text-muted-foreground py-4">加载中...</p>
          ) : evidences.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">暂无证据</p>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">#</th>
                    <th className="px-4 py-3 text-left font-medium">名称</th>
                    <th className="px-4 py-3 text-left font-medium">类型</th>
                    <th className="px-4 py-3 text-left font-medium">说明</th>
                    <th className="px-4 py-3 text-left font-medium">大小</th>
                    <th className="px-4 py-3 text-left font-medium">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {evidences.map((e, idx) => (
                    <tr key={e.id} className="border-t">
                      <td className="px-4 py-3 text-muted-foreground">{idx + 1}</td>
                      <td className="px-4 py-3 font-medium">{e.title}</td>
                      <td className="px-4 py-3">{EVIDENCE_TYPES[e.evidence_type] || e.evidence_type}</td>
                      <td className="px-4 py-3 text-muted-foreground">{e.description || "-"}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {e.file_size ? `${(e.file_size / 1024).toFixed(1)} KB` : "-"}
                      </td>
                      <td className="px-4 py-3">
                        <button onClick={() => deleteEvidence(e.id)} className="text-sm text-destructive hover:underline">
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === "AI分析" && (
        <div className="space-y-4">
          {(caseData.ai_analysis ? caseData.ai_analysis : aiResult) ? (
            <AnalysisDisplay data={(caseData.ai_analysis || aiResult) as Record<string, unknown>} />
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">尚未进行AI分析</p>
              <button
                onClick={fetchAnalysis}
                disabled={aiLoading}
                className="rounded-md bg-primary px-6 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {aiLoading ? "分析中..." : "开始AI分析"}
              </button>
            </div>
          )}
          {aiLoading && (
            <p className="text-center text-sm text-muted-foreground">AI正在分析案件，请稍候...</p>
          )}
        </div>
      )}
    </div>
  );
}
