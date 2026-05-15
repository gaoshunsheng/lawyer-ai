"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { DOC_STATUSES } from "@/lib/constants";
import type { DocumentItem } from "@/types";

export default function DocumentEditorPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const router = useRouter();
  const [doc, setDoc] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatedHtml, setGeneratedHtml] = useState("");
  const [instructions, setInstructions] = useState("");
  const eventSourceRef = useRef<AbortController | null>(null);

  // Version history state
  const [versions, setVersions] = useState<DocumentItem[]>([]);
  const [versionsOpen, setVersionsOpen] = useState(false);
  const [diffData, setDiffData] = useState<{
    old_version: string;
    new_version: string;
    diffs: { type: "added" | "removed"; content: string }[];
  } | null>(null);
  const [diffLoading, setDiffLoading] = useState(false);
  const [rollbackLoading, setRollbackLoading] = useState<string | null>(null);

  // Search-in-context (插入法规) state
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState<"law" | "case" | "all">("all");
  const [searchResults, setSearchResults] = useState<{
    laws: { id: string; title: string; law_type: string }[];
    cases: { id: string; case_name: string; case_type: string }[];
  } | null>(null);
  const [searching, setSearching] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  // Batch generate state
  const [batchDialogOpen, setBatchDialogOpen] = useState(false);
  const [batchRows, setBatchRows] = useState<Record<string, string>[]>([{}]);
  const [batchGenerating, setBatchGenerating] = useState(false);

  const fetchDoc = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<DocumentItem>(`/documents/${id}`, token);
      setDoc(data);
    } catch {
      router.push("/documents");
    } finally {
      setLoading(false);
    }
  }, [token, id, router]);

  useEffect(() => { fetchDoc(); }, [fetchDoc]);

  // Fetch version history
  const fetchVersions = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<DocumentItem[]>(`/documents/${id}/versions`, token);
      setVersions(data);
    } catch {
      // Silently fail — version panel is optional
    }
  }, [token, id]);

  useEffect(() => {
    if (versionsOpen) fetchVersions();
  }, [versionsOpen, fetchVersions]);

  // Toast auto-dismiss
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2500);
    return () => clearTimeout(t);
  }, [toast]);

  // Version diff handler
  const handleViewDiff = async (targetId: string) => {
    if (!token) return;
    setDiffLoading(true);
    setDiffData(null);
    try {
      const data = await api.get<{
        old_version: string;
        new_version: string;
        diffs: { type: "added" | "removed"; content: string }[];
      }>(`/documents/${id}/versions/${targetId}/diff`, token);
      setDiffData(data);
    } catch {
      setToast("获取差异失败");
    } finally {
      setDiffLoading(false);
    }
  };

  // Version rollback handler
  const handleRollback = async (targetId: string) => {
    if (!token) return;
    if (!confirm("确定要回滚到此版本吗？将创建一个新版本。")) return;
    setRollbackLoading(targetId);
    try {
      const newDoc = await api.post<DocumentItem>(`/documents/${id}/versions/${targetId}/rollback`, {}, token);
      setDoc(newDoc);
      setToast("已成功回滚");
      fetchVersions();
    } catch {
      setToast("回滚失败");
    } finally {
      setRollbackLoading(null);
    }
  };

  // Search-in-context handler
  const handleSearchInContext = async () => {
    if (!token || !searchQuery.trim()) return;
    setSearching(true);
    setSearchResults(null);
    try {
      const data = await api.post<{
        laws: { id: string; title: string; law_type: string }[];
        cases: { id: string; case_name: string; case_type: string }[];
      }>(`/documents/search-in-context?query=${encodeURIComponent(searchQuery)}&search_type=${searchType}`, {}, token);
      setSearchResults(data);
    } catch {
      setToast("搜索失败");
    } finally {
      setSearching(false);
    }
  };

  // Copy reference to clipboard
  const handleCopyReference = (item: { id: string; title?: string; case_name?: string }, type: "law" | "case") => {
    const ref = type === "law" ? `[法规] ${item.title}` : `[案例] ${item.case_name}`;
    navigator.clipboard.writeText(ref).then(() => {
      setToast("已复制法规引用");
    }).catch(() => {
      setToast("复制失败");
    });
  };

  // Batch generate handlers
  const handleAddBatchRow = () => {
    setBatchRows([...batchRows, {}]);
  };

  const handleBatchRowChange = (index: number, key: string, value: string) => {
    const updated = [...batchRows];
    updated[index] = { ...updated[index], [key]: value };
    setBatchRows(updated);
  };

  const handleRemoveBatchRow = (index: number) => {
    if (batchRows.length <= 1) return;
    setBatchRows(batchRows.filter((_, i) => i !== index));
  };

  const handleBatchGenerate = async () => {
    if (!token || !doc?.template_id) return;
    setBatchGenerating(true);
    try {
      const result = await api.post<{ created_ids: string[]; count: number }>(
        "/documents/batch-generate",
        { template_id: doc.template_id, variable_sets: batchRows },
        token
      );
      setToast(`批量生成成功，共 ${result.count} 份文书`);
      setBatchDialogOpen(false);
      setBatchRows([{}]);
    } catch {
      setToast("批量生成失败");
    } finally {
      setBatchGenerating(false);
    }
  };

  // Get template variable fields from doc
  const getTemplateVariables = (): string[] => {
    if (!doc?.variables) return [];
    return Object.keys(doc.variables as Record<string, string>);
  };

  const handleGenerate = () => {
    if (!token) return;
    setGenerating(true);
    setGeneratedHtml("");

    const controller = new AbortController();
    eventSourceRef.current = controller;

    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/documents/${id}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ instructions: instructions || null }),
      signal: controller.signal,
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Generation failed");
        const reader = res.body?.getReader();
        if (!reader) return;

        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data === "[DONE]") { setGenerating(false); return; }
              try {
                const parsed = JSON.parse(data);
                if (parsed.status === "complete" && parsed.content?.html) {
                  setGeneratedHtml(parsed.content.html);
                }
              } catch {}
            }
          }
        }
        setGenerating(false);
      })
      .catch(() => setGenerating(false));
  };

  const handleExport = async () => {
    if (!token) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/documents/${id}/export`,
        {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}` },
        }
      );
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${doc?.title || "document"}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {}
  };

  // Render filled template preview
  const renderPreview = (): string => {
    if (!doc?.content) return "";
    let text: string = String(doc.content.raw || "");
    if (doc.content.variables) {
      for (const [k, v] of Object.entries(doc.content.variables as Record<string, string>)) {
        text = text.replace(new RegExp(`\\{\\{\\s*${k}\\s*\\}\\}`, "g"), v);
      }
    }
    return text;
  };

  if (loading) return <p className="p-6 text-center text-muted-foreground">加载中...</p>;
  if (!doc) return <p className="p-6 text-center text-muted-foreground">文书不存在</p>;

  const preview = renderPreview();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => router.push("/documents")} className="text-sm text-muted-foreground hover:text-foreground mb-1">
            ← 返回文书列表
          </button>
          <h1 className="text-2xl font-bold">{doc.title}</h1>
          <p className="text-sm text-muted-foreground">
            {DOC_STATUSES[doc.status] || doc.status} · v{doc.version}
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button onClick={handleGenerate} disabled={generating}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
            {generating ? "生成中..." : "AI 生成"}
          </button>
          <button onClick={() => setSearchDialogOpen(true)}
            className="rounded-md border px-4 py-2 text-sm hover:bg-accent">
            插入法规
          </button>
          {doc.template_id && (
            <button onClick={() => setBatchDialogOpen(true)}
              className="rounded-md border px-4 py-2 text-sm hover:bg-accent">
              批量生成
            </button>
          )}
          <button onClick={handleExport}
            className="rounded-md border px-4 py-2 text-sm hover:bg-accent">
            导出
          </button>
        </div>
      </div>

      {/* AI instructions */}
      <div className="rounded-lg border p-4 space-y-2">
        <label className="text-sm font-medium">AI 生成指令（可选）</label>
        <textarea
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          rows={2}
          placeholder="如：请详细阐述事实与理由部分，引用《劳动合同法》相关条款..."
          className="w-full rounded-md border px-3 py-2 text-sm bg-background"
        />
      </div>

      {/* Preview area */}
      <div className="rounded-lg border">
        <div className="px-4 py-3 bg-muted/50 border-b font-medium text-sm">文书预览</div>
        <div className="p-6 min-h-[400px]">
          {generatedHtml ? (
            <div dangerouslySetInnerHTML={{ __html: generatedHtml }} />
          ) : preview ? (
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{preview}</pre>
          ) : (
            <p className="text-center text-muted-foreground py-12">暂无内容，点击"AI 生成"开始</p>
          )}
        </div>
      </div>

      {/* Variable summary */}
      {doc.variables && Object.keys(doc.variables).length > 0 && (
        <div className="rounded-lg border p-4">
          <h3 className="text-sm font-medium mb-2">已填写变量</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {Object.entries(doc.variables as Record<string, string>).map(([k, v]) => (
              <div key={k} className="text-sm">
                <span className="text-muted-foreground">{k}: </span>
                <span className="font-medium">{v || "(空)"}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Version History Panel ── */}
      <div className="rounded-lg border">
        <button
          onClick={() => setVersionsOpen(!versionsOpen)}
          className="w-full flex items-center justify-between px-4 py-3 bg-muted/50 hover:bg-muted/70 transition"
        >
          <span className="font-medium text-sm">版本历史</span>
          <span className="text-xs text-muted-foreground">{versionsOpen ? "收起" : "展开"}</span>
        </button>

        {versionsOpen && (
          <div className="divide-y">
            {versions.length === 0 && (
              <p className="p-4 text-sm text-muted-foreground text-center">暂无版本记录</p>
            )}
            {versions.map((v) => {
              const isCurrent = v.version === doc.version;
              return (
                <div key={v.id} className="flex items-center justify-between px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">v{v.version}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(v.created_at).toLocaleString("zh-CN", {
                        timeZone: "Asia/Shanghai",
                        year: "numeric",
                        month: "2-digit",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      }).replace(/\//g, "-")}
                    </span>
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      v.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : v.status === "draft"
                        ? "bg-gray-100 text-gray-600"
                        : v.status === "generating"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-blue-100 text-blue-700"
                    }`}>
                      {DOC_STATUSES[v.status] || v.status}
                    </span>
                    {isCurrent && (
                      <span className="text-xs text-primary font-medium">当前版本</span>
                    )}
                  </div>
                  {!isCurrent && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleViewDiff(v.id)}
                        disabled={diffLoading}
                        className="rounded border px-2 py-1 text-xs hover:bg-accent disabled:opacity-50"
                      >
                        对比
                      </button>
                      <button
                        onClick={() => handleRollback(v.id)}
                        disabled={rollbackLoading === v.id}
                        className="rounded border px-2 py-1 text-xs hover:bg-accent disabled:opacity-50"
                      >
                        {rollbackLoading === v.id ? "回滚中..." : "回滚"}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}

            {/* Inline diff view */}
            {diffLoading && (
              <div className="p-4 text-center text-sm text-muted-foreground">加载差异中...</div>
            )}
            {diffData && !diffLoading && (
              <div className="border-t">
                <div className="px-4 py-2 bg-muted/30 text-xs text-muted-foreground">
                  版本差异: v{diffData.old_version} → v{diffData.new_version}
                </div>
                <div className="p-4 max-h-[300px] overflow-y-auto space-y-1">
                  {diffData.diffs.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center">无差异</p>
                  )}
                  {diffData.diffs.map((d, i) => (
                    <div
                      key={i}
                      className={`px-3 py-1 rounded text-sm font-mono whitespace-pre-wrap ${
                        d.type === "added"
                          ? "bg-green-50 text-green-800 border-l-4 border-green-400"
                          : "bg-red-50 text-red-800 border-l-4 border-red-400"
                      }`}
                    >
                      <span className="mr-2 font-bold">{d.type === "added" ? "+" : "-"}</span>
                      {d.content}
                    </div>
                  ))}
                  <div className="flex justify-end pt-2">
                    <button
                      onClick={() => setDiffData(null)}
                      className="text-xs text-muted-foreground hover:text-foreground"
                    >
                      关闭差异
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Search-in-Context (插入法规) Dialog ── */}
      {searchDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-background rounded-lg shadow-lg w-full max-w-lg mx-4 max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <h3 className="font-medium">插入法规</h3>
              <button onClick={() => { setSearchDialogOpen(false); setSearchResults(null); setSearchQuery(""); }}
                className="text-muted-foreground hover:text-foreground text-lg leading-none">&times;</button>
            </div>

            <div className="p-4 space-y-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") handleSearchInContext(); }}
                  placeholder="输入关键词搜索法规或案例..."
                  className="flex-1 rounded-md border px-3 py-2 text-sm bg-background"
                />
                <select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value as "law" | "case" | "all")}
                  className="rounded-md border px-2 py-2 text-sm bg-background"
                >
                  <option value="all">全部</option>
                  <option value="law">法规</option>
                  <option value="case">案例</option>
                </select>
                <button
                  onClick={handleSearchInContext}
                  disabled={searching || !searchQuery.trim()}
                  className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  {searching ? "搜索中..." : "搜索"}
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 pb-4">
              {searchResults && (
                <div className="space-y-2">
                  {searchResults.laws.length === 0 && searchResults.cases.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">未找到相关结果</p>
                  )}
                  {searchResults.laws.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground mb-1">法规</p>
                      {searchResults.laws.map((law) => (
                        <div key={law.id}
                          onClick={() => handleCopyReference(law, "law")}
                          className="flex items-center justify-between rounded-md border px-3 py-2 mb-1 cursor-pointer hover:bg-accent transition">
                          <div>
                            <span className="text-sm font-medium">{law.title}</span>
                            {law.law_type && (
                              <span className="ml-2 text-xs text-muted-foreground">({law.law_type})</span>
                            )}
                          </div>
                          <span className="text-xs text-primary">点击复制</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {searchResults.cases.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs font-medium text-muted-foreground mb-1">案例</p>
                      {searchResults.cases.map((c) => (
                        <div key={c.id}
                          onClick={() => handleCopyReference(c, "case")}
                          className="flex items-center justify-between rounded-md border px-3 py-2 mb-1 cursor-pointer hover:bg-accent transition">
                          <div>
                            <span className="text-sm font-medium">{c.case_name}</span>
                            {c.case_type && (
                              <span className="ml-2 text-xs text-muted-foreground">({c.case_type})</span>
                            )}
                          </div>
                          <span className="text-xs text-primary">点击复制</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Batch Generate (批量生成) Dialog ── */}
      {batchDialogOpen && doc.template_id && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-background rounded-lg shadow-lg w-full max-w-3xl mx-4 max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <h3 className="font-medium">批量生成</h3>
              <button onClick={() => { setBatchDialogOpen(false); setBatchRows([{}]); }}
                className="text-muted-foreground hover:text-foreground text-lg leading-none">&times;</button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {getTemplateVariables().length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">模板无变量，无需批量设置</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="px-2 py-2 text-left text-xs font-medium text-muted-foreground w-10">#</th>
                        {getTemplateVariables().map((key) => (
                          <th key={key} className="px-2 py-2 text-left text-xs font-medium text-muted-foreground">
                            {key}
                          </th>
                        ))}
                        <th className="px-2 py-2 w-10"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {batchRows.map((row, idx) => (
                        <tr key={idx} className="border-b last:border-b-0">
                          <td className="px-2 py-2 text-muted-foreground">{idx + 1}</td>
                          {getTemplateVariables().map((key) => (
                            <td key={key} className="px-2 py-1">
                              <input
                                type="text"
                                value={row[key] || ""}
                                onChange={(e) => handleBatchRowChange(idx, key, e.target.value)}
                                placeholder={key}
                                className="w-full rounded border px-2 py-1 text-sm bg-background"
                              />
                            </td>
                          ))}
                          <td className="px-2 py-1">
                            <button
                              onClick={() => handleRemoveBatchRow(idx)}
                              disabled={batchRows.length <= 1}
                              className="text-red-500 hover:text-red-700 disabled:opacity-30 text-xs"
                            >
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

            <div className="flex items-center justify-between px-4 py-3 border-t">
              <button
                onClick={handleAddBatchRow}
                className="rounded-md border px-3 py-1.5 text-sm hover:bg-accent"
              >
                + 添加行
              </button>
              <div className="flex gap-2">
                <button
                  onClick={() => { setBatchDialogOpen(false); setBatchRows([{}]); }}
                  className="rounded-md border px-4 py-2 text-sm hover:bg-accent"
                >
                  取消
                </button>
                <button
                  onClick={handleBatchGenerate}
                  disabled={batchGenerating || getTemplateVariables().length === 0}
                  className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  {batchGenerating ? "生成中..." : "生成"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast notification ── */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 rounded-lg bg-foreground text-background px-4 py-2 text-sm shadow-lg animate-in fade-in slide-in-from-bottom-2">
          {toast}
        </div>
      )}
    </div>
  );
}
