"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import Link from "next/link";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border bg-background p-6 space-y-4">
      <h2 className="text-xl font-semibold text-center">登录</h2>
      {error && <p className="text-sm text-destructive bg-destructive/10 rounded px-3 py-2">{error}</p>}
      <div>
        <label className="text-sm font-medium">用户名</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} required className="mt-1 w-full rounded-md border px-3 py-2" />
      </div>
      <div>
        <label className="text-sm font-medium">密码</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="mt-1 w-full rounded-md border px-3 py-2" />
      </div>
      <button type="submit" disabled={loading} className="w-full rounded-md bg-primary py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
        {loading ? "登录中..." : "登录"}
      </button>
      <p className="text-center text-sm text-muted-foreground">
        没有账户？ <Link href="/register" className="text-primary hover:underline">注册</Link>
      </p>
    </form>
  );
}
