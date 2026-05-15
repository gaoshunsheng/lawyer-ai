"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { DOC_STATUSES } from "@/lib/constants";
import type { DocumentItem } from "@/types";

export default function DocumentsPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");

  const fetchDocs = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "20");
      if (statusFilter) params.set("status", statusFilter);
      const data = await api.get<{ items: DocumentItem[]; total: number }>(
        `/documents?${params.toString()}`,
        token
      );
      setDocs(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [token, page, statusFilter]);

  useEffect(() => { fetchDocs(); }, [fetchDocs]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">文书中心</h1>
          <p className="text-sm text-muted-foreground mt-1">共 {total} 份文书</p>
        </div>
        <div className="flex gap-2">
          <Link href="/documents/templates" className="rounded-md border px-4 py-2 text-sm hover:bg-accent">
            模板库
          </Link>
          <Link href="/documents/new" className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90">
            + 新建文书
          </Link>
        </div>
      </div>

      <select
        value={statusFilter}
        onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
        className="rounded-md border px-3 py-2 text-sm bg-background w-40"
      >
        <option value="">全部状态</option>
        {Object.entries(DOC_STATUSES).map(([k, v]) => (
          <option key={k} value={k}>{v}</option>
        ))}
      </select>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : docs.length === 0 ? (
        <p className="text-center text-muted-foreground py-8">暂无文书</p>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left font-medium">标题</th>
                <th className="px-4 py-3 text-left font-medium">状态</th>
                <th className="px-4 py-3 text-left font-medium">版本</th>
                <th className="px-4 py-3 text-left font-medium">创建时间</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((d) => (
                <tr key={d.id} className="border-t hover:bg-muted/30 cursor-pointer" onClick={() => router.push(`/documents/${d.id}`)}>
                  <td className="px-4 py-3 font-medium">{d.title}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      d.status === "completed" ? "bg-green-100 text-green-700" :
                      d.status === "generating" ? "bg-yellow-100 text-yellow-700" :
                      d.status === "exported" ? "bg-blue-100 text-blue-700" :
                      "bg-gray-100 text-gray-700"
                    }`}>
                      {DOC_STATUSES[d.status] || d.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">v{d.version}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(d.created_at).toLocaleDateString("zh-CN")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
