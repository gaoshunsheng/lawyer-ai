"use client";

import { useState } from "react";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";

interface Case {
  id: string;
  case_name: string;
  case_type: string | null;
  court: string | null;
  judgment_date: string | null;
  result: string | null;
  summary: string | null;
}

export function CaseSearch() {
  const { token } = useAuth();
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<Case[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!keyword.trim() || !token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ keyword, page: "1", page_size: "20" });
      const data = await api.get<{ items: Case[]; total: number }>(`/knowledge/cases?${params}`, token);
      setResults(data.items || []);
      setTotal(data.total || 0);
    } catch {
      console.error("搜索失败");
    } finally {
      setLoading(false);
    }
  };

  const resultLabels: Record<string, string> = {
    win: "胜诉",
    lose: "败诉",
    partial: "部分胜诉",
  };

  const resultColors: Record<string, string> = {
    win: "bg-green-100 text-green-700",
    lose: "bg-red-100 text-red-700",
    partial: "bg-yellow-100 text-yellow-700",
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="搜索案例..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          className="flex-1 rounded-md border px-4 py-2"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="rounded-md bg-primary px-6 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? "搜索中..." : "搜索"}
        </button>
      </div>

      {total > 0 && (
        <p className="text-sm text-muted-foreground">共 {total} 条结果</p>
      )}

      <div className="space-y-3">
        {results.map((caseItem) => (
          <a
            key={caseItem.id}
            href={`/knowledge/cases/${caseItem.id}`}
            className="block rounded-lg border p-4 hover:bg-accent"
          >
            <div className="flex items-center gap-2">
              {caseItem.result && (
                <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${resultColors[caseItem.result] || ""}`}>
                  {resultLabels[caseItem.result] || caseItem.result}
                </span>
              )}
              {caseItem.case_type && (
                <span className="text-sm text-muted-foreground">{caseItem.case_type}</span>
              )}
            </div>
            <h3 className="mt-2 font-medium">{caseItem.case_name}</h3>
            <div className="mt-1 flex gap-4 text-sm text-muted-foreground">
              {caseItem.court && <span>{caseItem.court}</span>}
              {caseItem.judgment_date && <span>{caseItem.judgment_date}</span>}
            </div>
            {caseItem.summary && (
              <p className="mt-2 text-sm text-muted-foreground line-clamp-2">{caseItem.summary}</p>
            )}
          </a>
        ))}
      </div>
    </div>
  );
}
