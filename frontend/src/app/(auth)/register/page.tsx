"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import Link from "next/link";

export default function RegisterPage() {
  const [form, setForm] = useState({ username: "", email: "", password: "", real_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form.username, form.email, form.password, form.real_name || undefined);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "注册失败");
    } finally {
      setLoading(false);
    }
  };

  const update = (k: string, v: string) => setForm((prev) => ({ ...prev, [k]: v }));

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border bg-background p-6 space-y-4">
      <h2 className="text-xl font-semibold text-center">注册</h2>
      {error && <p className="text-sm text-destructive bg-destructive/10 rounded px-3 py-2">{error}</p>}
      <div>
        <label className="text-sm font-medium">用户名</label>
        <input value={form.username} onChange={(e) => update("username", e.target.value)} required className="mt-1 w-full rounded-md border px-3 py-2" />
      </div>
      <div>
        <label className="text-sm font-medium">邮箱</label>
        <input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} required className="mt-1 w-full rounded-md border px-3 py-2" />
      </div>
      <div>
        <label className="text-sm font-medium">密码</label>
        <input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} required minLength={8} className="mt-1 w-full rounded-md border px-3 py-2" />
      </div>
      <div>
        <label className="text-sm font-medium">姓名 (可选)</label>
        <input value={form.real_name} onChange={(e) => update("real_name", e.target.value)} className="mt-1 w-full rounded-md border px-3 py-2" />
      </div>
      <button type="submit" disabled={loading} className="w-full rounded-md bg-primary py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
        {loading ? "注册中..." : "注册"}
      </button>
      <p className="text-center text-sm text-muted-foreground">
        已有账户？ <Link href="/login" className="text-primary hover:underline">登录</Link>
      </p>
    </form>
  );
}
