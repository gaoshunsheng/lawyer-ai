"use client";

import { useState } from "react";

const calcTypes = [
  { value: "illegal_termination", label: "违法解除(2N)" },
  { value: "overtime", label: "加班费" },
  { value: "annual_leave", label: "年休假补偿" },
  { value: "work_injury", label: "工伤赔偿" },
];

export default function CalculatorPage() {
  const [calcType, setCalcType] = useState("illegal_termination");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [monthlySalary, setMonthlySalary] = useState("");
  const [workYears, setWorkYears] = useState("");
  const [city, setCity] = useState("全国");

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/calculator/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ calc_type: calcType, params: { monthly_salary: Number(monthlySalary), work_years: Number(workYears), city } }),
      });
      setResult(await res.json());
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold">赔偿计算器</h1>

      <div className="space-y-4 rounded-lg border p-6">
        <div>
          <label className="text-sm font-medium">计算类型</label>
          <select value={calcType} onChange={(e) => setCalcType(e.target.value)} className="mt-1 w-full rounded-md border px-3 py-2">
            {calcTypes.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm font-medium">月工资 (元)</label>
          <input type="number" value={monthlySalary} onChange={(e) => setMonthlySalary(e.target.value)} className="mt-1 w-full rounded-md border px-3 py-2" placeholder="10000" />
        </div>
        {(calcType === "illegal_termination" || calcType === "annual_leave") && (
          <div>
            <label className="text-sm font-medium">工作年限</label>
            <input type="number" value={workYears} onChange={(e) => setWorkYears(e.target.value)} className="mt-1 w-full rounded-md border px-3 py-2" placeholder="3" />
          </div>
        )}
        <button onClick={handleCalculate} disabled={loading || !monthlySalary} className="rounded-md bg-primary px-6 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
          {loading ? "计算中..." : "计算"}
        </button>
      </div>

      {result && !result.error && (
        <div className="rounded-lg border p-6 space-y-4">
          <div className="text-3xl font-bold text-primary">{result.result?.toLocaleString()} 元</div>
          {result.steps?.map((s: string, i: number) => <p key={i} className="text-sm">{s}</p>)}
          {result.basis?.map((b: string, i: number) => <p key={i} className="text-xs text-muted-foreground">{b}</p>)}
        </div>
      )}
    </div>
  );
}
