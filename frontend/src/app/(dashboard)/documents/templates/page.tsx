"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { DOC_CATEGORIES } from "@/lib/constants";
import type { TemplateItem } from "@/types";

export default function TemplatesPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");

  const fetchTemplates = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = category ? `?category=${category}` : "";
      const data = await api.get<TemplateItem[]>(`/document-templates${params}`, token);
      setTemplates(data);
    } finally {
      setLoading(false);
    }
  }, [token, category]);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const categories = ["全部", ...Object.values(DOC_CATEGORIES)];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">文书模板库</h1>
          <p className="text-sm text-muted-foreground mt-1">{templates.length} 个模板</p>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat === "全部" ? "" : cat)}
            className={`rounded-full px-3 py-1 text-sm ${
              (cat === "全部" && !category) || cat === category
                ? "bg-primary text-primary-foreground"
                : "border hover:bg-accent"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : templates.length === 0 ? (
        <p className="text-center text-muted-foreground py-8">暂无模板</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t) => (
            <div key={t.id} className="rounded-lg border p-5 space-y-3 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{t.name}</h3>
                <span className="text-xs rounded-full bg-accent px-2 py-0.5">{t.category}</span>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-3 font-mono text-xs whitespace-pre-wrap">
                {t.content_template.slice(0, 150)}...
              </p>
              <div className="flex flex-wrap gap-1">
                {t.variables_schema?.variables?.slice(0, 4).map((v: { name: string; label: string }) => (
                  <span key={v.name} className="text-xs bg-muted rounded px-1.5 py-0.5">{v.label}</span>
                ))}
                {(t.variables_schema?.variables?.length || 0) > 4 && (
                  <span className="text-xs text-muted-foreground">+{t.variables_schema.variables.length - 4}</span>
                )}
              </div>
              <button
                onClick={() => router.push(`/documents/new?template=${t.id}`)}
                className="w-full rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
              >
                使用此模板
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
