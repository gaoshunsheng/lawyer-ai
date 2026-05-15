"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import type { CaseItem, GanttData } from "@/types";
import GanttChart from "@/components/gantt/gantt-chart";

const TEMPLATES = [
  { type: "labor_arbitration", label: "劳动仲裁流程", description: "包含劳动仲裁各阶段流程节点" },
  { type: "first_instance", label: "一审流程", description: "包含一审诉讼全流程节点" },
  { type: "second_instance", label: "二审流程", description: "包含二审诉讼全流程节点" },
  { type: "non_litigation", label: "非诉业务", description: "包含非诉业务通用流程节点" },
] as const;

export default function GanttPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const router = useRouter();

  const [caseData, setCaseData] = useState<CaseItem | null>(null);
  const [ganttData, setGanttData] = useState<GanttData | null>(null);
  const [loading, setLoading] = useState(true);
  const [templateLoading, setTemplateLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchCase = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<CaseItem>(`/cases/${id}`, token);
      setCaseData(data);
    } catch {
      router.push("/cases");
    }
  }, [token, id, router]);

  const fetchGantt = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<GanttData | null>(`/cases/${id}/gantt`, token);
      setGanttData(data);
    } catch {
      setError("加载甘特图数据失败");
    } finally {
      setLoading(false);
    }
  }, [token, id]);

  useEffect(() => {
    fetchCase();
  }, [fetchCase]);

  useEffect(() => {
    fetchGantt();
  }, [fetchGantt]);

  const applyTemplate = async (templateType: string) => {
    if (!token || templateLoading) return;
    setTemplateLoading(templateType);
    setError(null);
    try {
      const data = await api.post<GanttData>(
        `/cases/${id}/gantt/template`,
        { template_type: templateType },
        token
      );
      setGanttData(data);
    } catch {
      setError("应用模板失败，请重试");
    } finally {
      setTemplateLoading(null);
    }
  };

  if (loading) {
    return <p className="p-6 text-center text-muted-foreground">加载中...</p>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => router.push(`/cases/${id}`)}
          className="text-sm text-muted-foreground hover:text-foreground mb-1"
        >
          &larr; 返回案件详情
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">
              甘特图{caseData ? ` - ${caseData.title}` : ""}
            </h1>
            {caseData && (
              <p className="text-sm text-muted-foreground font-mono">{caseData.case_number}</p>
            )}
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* No data: template selection */}
      {ganttData === null && !loading && (
        <div className="rounded-lg border p-5 space-y-4">
          <div>
            <h2 className="text-lg font-semibold">选择模板</h2>
            <p className="text-sm text-muted-foreground mt-1">
              该案件暂无甘特图数据，请选择一个流程模板快速开始
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {TEMPLATES.map((tpl) => (
              <button
                key={tpl.type}
                onClick={() => applyTemplate(tpl.type)}
                disabled={templateLoading !== null}
                className="rounded-lg border p-4 text-left hover:border-primary hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">{tpl.label}</span>
                  {templateLoading === tpl.type && (
                    <span className="text-xs text-muted-foreground">加载中...</span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">{tpl.description}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Has data: render chart */}
      {ganttData && ganttData.nodes.length > 0 && (
        <GanttChart data={ganttData} caseId={id} token={token!} />
      )}

      {/* Empty data after template applied */}
      {ganttData && ganttData.nodes.length === 0 && (
        <div className="rounded-lg border p-8 text-center text-muted-foreground">
          <p>模板数据为空，请尝试其他模板</p>
        </div>
      )}
    </div>
  );
}
