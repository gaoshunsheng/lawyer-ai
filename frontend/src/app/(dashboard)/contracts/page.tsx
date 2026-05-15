"use client";

import { useState } from "react";
import { useAuth } from "@/providers/auth-provider";

interface RiskItem {
  level: "high" | "medium" | "low";
  description: string;
  clause?: string;
  suggestion?: string;
}

interface ReviewReport {
  id: string;
  overall_score?: number;
  compliance?: { passed: string[]; missing: string[] };
  risks?: RiskItem[];
  suggestions?: string[];
  summary?: string;
}

export default function ContractsPage() {
  const { token } = useAuth();
  const [mode, setMode] = useState<"upload" | "paste">("paste");
  const [contractText, setContractText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [concerns, setConcerns] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<ReviewReport | null>(null);
  const [error, setError] = useState("");

  const handleReview = async () => {
    if (!token) return;
    setError("");
    setReport(null);

    if (mode === "paste" && !contractText.trim()) {
      setError("请粘贴合同文本"); return;
    }
    if (mode === "upload" && !file) {
      setError("请选择合同文件"); return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      if (mode === "paste") {
        formData.append("text", contractText);
      } else if (file) {
        formData.append("file", file);
      }
      if (concerns) formData.append("concerns", concerns);

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/contracts/review`,
        {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}` },
          body: formData,
        }
      );
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "审查失败");
      }
      const data = await res.json();
      setReport(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "审查请求失败");
    } finally {
      setLoading(false);
    }
  };

  const riskBadgeColor = (level: string) => {
    switch (level) {
      case "high": return "bg-red-100 text-red-700";
      case "medium": return "bg-yellow-100 text-yellow-700";
      case "low": return "bg-blue-100 text-blue-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">合同审查</h1>
        <p className="text-sm text-muted-foreground mt-1">上传合同文件或粘贴合同文本，AI自动进行5维度审查</p>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setMode("paste")}
          className={`rounded-md px-4 py-2 text-sm ${mode === "paste" ? "bg-primary text-primary-foreground" : "border hover:bg-accent"}`}
        >
          粘贴文本
        </button>
        <button
          onClick={() => setMode("upload")}
          className={`rounded-md px-4 py-2 text-sm ${mode === "upload" ? "bg-primary text-primary-foreground" : "border hover:bg-accent"}`}
        >
          上传文件
        </button>
      </div>

      {error && <p className="text-sm text-destructive bg-destructive/10 rounded-md px-4 py-2">{error}</p>}

      <div className="rounded-lg border p-5 space-y-4">
        {mode === "paste" ? (
          <textarea
            value={contractText}
            onChange={(e) => setContractText(e.target.value)}
            rows={15}
            placeholder="在此粘贴劳动合同全文..."
            className="w-full rounded-md border px-4 py-3 text-sm bg-background font-mono"
          />
        ) : (
          <div className="space-y-2">
            <input
              type="file"
              accept=".txt,.doc,.docx,.pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="text-sm"
            />
            {file && <p className="text-sm text-muted-foreground">已选择: {file.name} ({(file.size / 1024).toFixed(1)} KB)</p>}
          </div>
        )}

        <div>
          <label className="text-sm font-medium">特别关注问题（可选）</label>
          <input
            type="text"
            value={concerns}
            onChange={(e) => setConcerns(e.target.value)}
            placeholder="如：试用期条款是否合法、竞业限制范围是否过大..."
            className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1"
          />
        </div>

        <button
          onClick={handleReview}
          disabled={loading}
          className="rounded-md bg-primary px-6 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? "审查中（约30秒）..." : "开始审查"}
        </button>
      </div>

      {/* Report */}
      {report && (
        <div className="space-y-4">
          <div className="rounded-lg border p-5 bg-primary/5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">审查报告</h2>
              {report.overall_score != null && (
                <span className={`text-2xl font-bold ${report.overall_score >= 80 ? "text-green-600" : report.overall_score >= 60 ? "text-yellow-600" : "text-red-600"}`}>
                  {report.overall_score}分
                </span>
              )}
            </div>
            {report.summary && <p className="text-sm text-muted-foreground mt-2">{report.summary}</p>}
          </div>

          {/* Compliance */}
          {report.compliance && (
            <div className="rounded-lg border p-5">
              <h3 className="font-semibold mb-3">合规性检查</h3>
              {report.compliance.missing?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-red-600">缺失条款：</p>
                  {report.compliance.missing.map((m: string, i: number) => (
                    <p key={i} className="text-sm text-red-700 bg-red-50 rounded px-3 py-1.5">⚠ {m}</p>
                  ))}
                </div>
              )}
              {report.compliance.passed?.length > 0 && (
                <div className="space-y-2 mt-3">
                  <p className="text-sm font-medium text-green-600">已满足：</p>
                  {report.compliance.passed.map((p: string, i: number) => (
                    <p key={i} className="text-sm text-green-700 bg-green-50 rounded px-3 py-1.5">✓ {p}</p>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Risks */}
          {report.risks && report.risks.length > 0 && (
            <div className="rounded-lg border p-5">
              <h3 className="font-semibold mb-3">风险条款（{report.risks.length}项）</h3>
              <div className="space-y-3">
                {report.risks.map((r: RiskItem, i: number) => (
                  <div key={i} className="flex gap-3 border-b pb-3 last:border-0">
                    <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${riskBadgeColor(r.level)}`}>
                      {r.level === "high" ? "高风险" : r.level === "medium" ? "中风险" : "低风险"}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm">{r.description}</p>
                      {r.clause && <p className="text-xs text-muted-foreground mt-1 font-mono">原文: {r.clause}</p>}
                      {r.suggestion && <p className="text-xs text-green-700 mt-1">建议: {r.suggestion}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Suggestions */}
          {report.suggestions && report.suggestions.length > 0 && (
            <div className="rounded-lg border p-5">
              <h3 className="font-semibold mb-3">修改建议</h3>
              <ul className="space-y-2">
                {report.suggestions.map((s: string, i: number) => (
                  <li key={i} className="text-sm flex gap-2">
                    <span className="text-primary shrink-0">→</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
