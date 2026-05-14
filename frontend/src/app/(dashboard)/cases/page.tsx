"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { CASE_TYPES, CASE_STATUSES } from "@/lib/constants";
import type { CaseItem } from "@/types";

export default function CasesPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [search, setSearch] = useState("");
  const searchTimeout = useRef<ReturnType<typeof setTimeout>>();

  const fetchCases = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "20");
      if (statusFilter) params.set("status", statusFilter);
      if (typeFilter) params.set("case_type", typeFilter);
      if (search) params.set("search", search);
      const data = await api.get<{ items: CaseItem[]; total: number }>(
        `/cases?${params.toString()}`,
        token
      );
      setCases(data.items);
      setTotal(data.total);
    } catch {
      // handled silently
    } finally {
      setLoading(false);
    }
  }, [token, page, statusFilter, typeFilter, search]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleSearch = (value: string) => {
    setSearch(value);
    clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      setPage(1);
    }, 300);
  };

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">案件管理</h1>
          <p className="text-sm text-muted-foreground mt-1">共 {total} 个案件</p>
        </div>
        <Link
          href="/cases/new"
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
        >
          + 新建案件
        </Link>
      </div>

      <div className="flex gap-3 flex-wrap">
        <input
          type="text"
          placeholder="搜索案件标题..."
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm bg-background w-64"
        />
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="rounded-md border px-3 py-2 text-sm bg-background"
        >
          <option value="">全部状态</option>
          {Object.entries(CASE_STATUSES).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          className="rounded-md border px-3 py-2 text-sm bg-background"
        >
          <option value="">全部类型</option>
          {Object.entries(CASE_TYPES).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : cases.length === 0 ? (
        <p className="text-center text-muted-foreground py-8">暂无案件</p>
      ) : (
        <>
          <div className="rounded-lg border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">案号</th>
                  <th className="px-4 py-3 text-left font-medium">标题</th>
                  <th className="px-4 py-3 text-left font-medium">类型</th>
                  <th className="px-4 py-3 text-left font-medium">状态</th>
                  <th className="px-4 py-3 text-left font-medium">标的金额</th>
                  <th className="px-4 py-3 text-left font-medium">创建时间</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr
                    key={c.id}
                    className="border-t hover:bg-muted/30 cursor-pointer"
                    onClick={() => router.push(`/cases/${c.id}`)}
                  >
                    <td className="px-4 py-3 font-mono text-xs">{c.case_number}</td>
                    <td className="px-4 py-3 font-medium">{c.title}</td>
                    <td className="px-4 py-3">{CASE_TYPES[c.case_type] || c.case_type}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                        c.status === "closed" || c.status === "archived"
                          ? "bg-green-100 text-green-700"
                          : c.status === "cancelled"
                          ? "bg-red-100 text-red-700"
                          : "bg-blue-100 text-blue-700"
                      }`}>
                        {CASE_STATUSES[c.status] || c.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {c.claim_amount != null ? `¥${c.claim_amount.toLocaleString()}` : "-"}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {new Date(c.created_at).toLocaleDateString("zh-CN")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-50"
              >
                上一页
              </button>
              <span className="text-sm text-muted-foreground">
                第 {page} / {totalPages} 页
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
