"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import type { TemplateItem, DocumentItem } from "@/types";

interface StepState {
  step: "select" | "fill" | "creating";
  template: TemplateItem | null;
  variables: Record<string, string>;
}

function NewDocumentContent() {
  const { token } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [state, setState] = useState<StepState>({ step: "select", template: null, variables: {} });
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  const fetchTemplates = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<TemplateItem[]>("/document-templates", token);
      setTemplates(data);
      const templateId = searchParams.get("template");
      if (templateId) {
        const tmpl = data.find((t) => t.id === templateId);
        if (tmpl) selectTemplate(tmpl);
      }
    } finally {
      setLoading(false);
    }
  }, [token, searchParams]);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const selectTemplate = (tmpl: TemplateItem) => {
    const vars: Record<string, string> = {};
    tmpl.variables_schema?.variables?.forEach((v) => {
      vars[v.name] = v.default || "";
    });
    setState({ step: "fill", template: tmpl, variables: vars });
    setTitle(tmpl.name);
  };

  const setVar = (name: string, value: string) => {
    setState((prev) => ({ ...prev, variables: { ...prev.variables, [name]: value } }));
  };

  const handleCreate = async () => {
    if (!state.template || !token) return;
    setError("");
    setState((prev) => ({ ...prev, step: "creating" }));
    try {
      const data = await api.post<DocumentItem>("/documents", {
        title: title.trim() || state.template.name,
        doc_type: state.template.doc_type,
        template_id: state.template.id,
        variables: state.variables,
      }, token);
      router.push(`/documents/${data.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "创建失败");
      setState((prev) => ({ ...prev, step: "fill" }));
    }
  };

  if (loading) return <p className="p-6 text-center text-muted-foreground">加载中...</p>;

  return (
    <div className="p-6 max-w-3xl space-y-6">
      <button onClick={() => router.push("/documents")} className="text-sm text-muted-foreground hover:text-foreground">
        ← 返回文书列表
      </button>
      <h1 className="text-2xl font-bold">新建文书</h1>

      {/* Step indicator */}
      <div className="flex items-center gap-3 text-sm">
        <span className={`rounded-full px-3 py-1 ${state.step === "select" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
          1. 选择模板
        </span>
        <span className="text-muted-foreground">→</span>
        <span className={`rounded-full px-3 py-1 ${state.step === "fill" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
          2. 填写信息
        </span>
      </div>

      {error && <p className="text-sm text-destructive bg-destructive/10 rounded-md px-4 py-2">{error}</p>}

      {/* Step 1: Select template */}
      {state.step === "select" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((t) => (
            <button
              key={t.id}
              onClick={() => selectTemplate(t)}
              className="text-left rounded-lg border p-4 hover:shadow-md hover:border-primary transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold">{t.name}</span>
                <span className="text-xs bg-accent rounded px-2 py-0.5">{t.category}</span>
              </div>
              <p className="text-xs text-muted-foreground font-mono line-clamp-2">{t.content_template.slice(0, 100)}</p>
            </button>
          ))}
        </div>
      )}

      {/* Step 2: Fill variables */}
      {state.step === "fill" && state.template && (
        <div className="space-y-4">
          <div className="rounded-lg border p-5">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs bg-accent rounded px-2 py-0.5">{state.template.category}</span>
              <span className="font-semibold">{state.template.name}</span>
            </div>
            <div>
              <label className="text-sm font-medium">文书标题</label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
            </div>
          </div>

          <div className="rounded-lg border p-5 space-y-4">
            <h2 className="font-semibold">填写信息</h2>
            {state.template.variables_schema?.variables?.map((v: { name: string; label: string; type: string; required: boolean }) => (
              <div key={v.name}>
                <label className="text-sm font-medium">
                  {v.label} {v.required && <span className="text-destructive">*</span>}
                </label>
                {v.type === "text" ? (
                  <textarea
                    value={state.variables[v.name] || ""}
                    onChange={(e) => setVar(v.name, e.target.value)}
                    rows={3}
                    className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1"
                  />
                ) : v.type === "date" ? (
                  <input
                    type="date"
                    value={state.variables[v.name] || ""}
                    onChange={(e) => setVar(v.name, e.target.value)}
                    className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1"
                  />
                ) : (
                  <input
                    type={v.type === "number" ? "number" : "text"}
                    value={state.variables[v.name] || ""}
                    onChange={(e) => setVar(v.name, e.target.value)}
                    className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1"
                  />
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button onClick={handleCreate} disabled={(state as StepState).step === "creating"}
              className="rounded-md bg-primary px-6 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
              {(state as StepState).step === "creating" ? "创建中..." : "创建文书"}
            </button>
            <button onClick={() => setState({ step: "select", template: null, variables: {} })}
              className="rounded-md border px-6 py-2 text-sm hover:bg-accent">
              重新选择
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function NewDocumentPage() {
  return (
    <Suspense fallback={<p className="p-6 text-center text-muted-foreground">加载中...</p>}>
      <NewDocumentContent />
    </Suspense>
  );
}
