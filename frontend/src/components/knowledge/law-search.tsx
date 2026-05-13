"use client";

import { useState } from "react";

interface Law {
  id: string;
  title: string;
  law_type: string;
  promulgating_body: string | null;
  effective_date: string | null;
  status: string;
}

export function LawSearch() {
  const [keyword, setKeyword] = useState("");
  const [lawType, setLawType] = useState("");
  const [results, setResults] = useState<Law[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!keyword.trim()) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ keyword, page: "1", page_size: "20" });
      if (lawType) params.set("law_type", lawType);
      // Token would come from auth context in production
      const res = await fetch(`/api/v1/knowledge/laws?${params}`);
      const data = await res.json();
      setResults(data.items || []);
      setTotal(data.total || 0);
    } catch {
      console.error("搜索失败");
    } finally {
      setLoading(false);
    }
  };

  const lawTypeLabels: Record<string, string> = {
    law: "法律",
    regulation: "行政法规",
    judicial_interpretation: "司法解释",
    local: "地方性法规",
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="搜索法律法规..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          className="flex-1 rounded-md border px-4 py-2"
        />
        <select
          value={lawType}
          onChange={(e) => setLawType(e.target.value)}
          className="rounded-md border px-4 py-2"
        >
          <option value="">全部类型</option>
          <option value="law">法律</option>
          <option value="regulation">行政法规</option>
          <option value="judicial_interpretation">司法解释</option>
          <option value="local">地方性法规</option>
        </select>
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
        {results.map((law) => (
          <a
            key={law.id}
            href={`/knowledge/laws/${law.id}`}
            className="block rounded-lg border p-4 hover:bg-accent"
          >
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                {lawTypeLabels[law.law_type] || law.law_type}
              </span>
              {law.status === "effective" && (
                <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">
                  有效
                </span>
              )}
            </div>
            <h3 className="mt-2 font-medium">{law.title}</h3>
            <div className="mt-1 flex gap-4 text-sm text-muted-foreground">
              {law.promulgating_body && <span>{law.promulgating_body}</span>}
              {law.effective_date && <span>施行: {law.effective_date}</span>}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
