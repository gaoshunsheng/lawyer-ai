"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { CASE_TYPES } from "@/lib/constants";
import type { CaseItem } from "@/types";

export default function NewCasePage() {
  const { token } = useAuth();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [caseType, setCaseType] = useState("labor_contract");
  const [pName, setPName] = useState("");
  const [pIdNumber, setPIdNumber] = useState("");
  const [pContact, setPContact] = useState("");
  const [dName, setDName] = useState("");
  const [dIdNumber, setDIdNumber] = useState("");
  const [dContact, setDContact] = useState("");
  const [claimAmount, setClaimAmount] = useState("");
  const [disputeFocus, setDisputeFocus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) { setError("请输入案件标题"); return; }
    setError("");
    setLoading(true);
    try {
      const data = await api.post<CaseItem>("/cases", {
        title: title.trim(),
        case_type: caseType,
        plaintiff: { name: pName.trim(), id_number: pIdNumber.trim(), contact: pContact.trim() },
        defendant: { name: dName.trim(), id_number: dIdNumber.trim(), contact: dContact.trim() },
        claim_amount: claimAmount ? parseFloat(claimAmount) : undefined,
        dispute_focus: disputeFocus ? disputeFocus.split(",").map((s) => s.trim()).filter(Boolean) : undefined,
      }, token!);
      router.push(`/cases/${data.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl">
      <button onClick={() => router.push("/cases")} className="text-sm text-muted-foreground hover:text-foreground mb-4">
        ← 返回案件列表
      </button>
      <h1 className="text-2xl font-bold mb-6">新建案件</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && <p className="text-sm text-destructive bg-destructive/10 rounded-md px-4 py-2">{error}</p>}

        <div className="rounded-lg border p-5 space-y-4">
          <h2 className="text-lg font-semibold">基本信息</h2>
          <div>
            <label className="text-sm font-medium">案件标题 *</label>
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" placeholder="如：张某某与XX公司劳动争议案" />
          </div>
          <div>
            <label className="text-sm font-medium">案件类型</label>
            <select value={caseType} onChange={(e) => setCaseType(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1">
              {Object.entries(CASE_TYPES).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">标的金额</label>
            <input type="number" value={claimAmount} onChange={(e) => setClaimAmount(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" placeholder="单位：元" />
          </div>
          <div>
            <label className="text-sm font-medium">争议焦点</label>
            <input type="text" value={disputeFocus} onChange={(e) => setDisputeFocus(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" placeholder="多个用逗号分隔，如：加班费,经济补偿金" />
          </div>
        </div>

        <div className="rounded-lg border p-5 space-y-4">
          <h2 className="text-lg font-semibold">原告信息</h2>
          <div>
            <label className="text-sm font-medium">姓名</label>
            <input type="text" value={pName} onChange={(e) => setPName(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">身份证号</label>
            <input type="text" value={pIdNumber} onChange={(e) => setPIdNumber(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">联系方式</label>
            <input type="text" value={pContact} onChange={(e) => setPContact(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
        </div>

        <div className="rounded-lg border p-5 space-y-4">
          <h2 className="text-lg font-semibold">被告信息</h2>
          <div>
            <label className="text-sm font-medium">名称（单位/个人）</label>
            <input type="text" value={dName} onChange={(e) => setDName(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">统一社会信用代码/身份证号</label>
            <input type="text" value={dIdNumber} onChange={(e) => setDIdNumber(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">联系方式</label>
            <input type="text" value={dContact} onChange={(e) => setDContact(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
        </div>

        <div className="flex gap-3">
          <button type="submit" disabled={loading} className="rounded-md bg-primary px-6 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
            {loading ? "创建中..." : "创建案件"}
          </button>
          <button type="button" onClick={() => router.push("/cases")} className="rounded-md border px-6 py-2 text-sm hover:bg-accent">
            取消
          </button>
        </div>
      </form>
    </div>
  );
}
