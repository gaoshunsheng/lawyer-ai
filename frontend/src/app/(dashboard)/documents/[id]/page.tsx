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
    let text = doc.content.raw || "";
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
        <div className="flex gap-2">
          <button onClick={handleGenerate} disabled={generating}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
            {generating ? "生成中..." : "AI 生成"}
          </button>
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
    </div>
  );
}
