"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api-client";
import { useAuth } from "@/providers/auth-provider";

interface ModelConfig {
  id: string;
  provider_id: string;
  model_name: string;
  model_type: string;
  capability: string | null;
  input_price_per_m: number | null;
  output_price_per_m: number | null;
  max_tokens: number | null;
  is_default: boolean;
  status: string;
}

export default function SettingsPage() {
  const { user, token } = useAuth();
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchModels = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<ModelConfig[]>("/models", token);
      setModels(data);
    } catch (err) {
      console.error("获取模型列表失败:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  const roleLabel: Record<string, string> = {
    platform_admin: "平台管理员",
    tenant_admin: "租户管理员",
    dept_admin: "部门管理员",
    lawyer: "律师",
    assistant: "助理",
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <h1 className="text-2xl font-bold">设置</h1>

      {/* 用户信息 */}
      <section className="rounded-lg border p-5 space-y-4">
        <h2 className="text-lg font-semibold">账户信息</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">用户名</p>
            <p className="font-medium mt-0.5">{user?.username}</p>
          </div>
          <div>
            <p className="text-muted-foreground">邮箱</p>
            <p className="font-medium mt-0.5">{user?.email}</p>
          </div>
          <div>
            <p className="text-muted-foreground">姓名</p>
            <p className="font-medium mt-0.5">{user?.real_name || "-"}</p>
          </div>
          <div>
            <p className="text-muted-foreground">角色</p>
            <p className="font-medium mt-0.5">{user ? roleLabel[user.role] || user.role : "-"}</p>
          </div>
          <div>
            <p className="text-muted-foreground">租户 ID</p>
            <p className="font-medium mt-0.5 font-mono text-xs">{user?.tenant_id || "-"}</p>
          </div>
          <div>
            <p className="text-muted-foreground">部门 ID</p>
            <p className="font-medium mt-0.5 font-mono text-xs">{user?.department_id || "-"}</p>
          </div>
        </div>
      </section>

      {/* 模型配置 */}
      <section className="rounded-lg border p-5 space-y-4">
        <h2 className="text-lg font-semibold">可用模型</h2>
        {loading ? (
          <p className="text-sm text-muted-foreground">加载中...</p>
        ) : models.length === 0 ? (
          <p className="text-sm text-muted-foreground">暂无可用模型配置</p>
        ) : (
          <div className="rounded-md border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium">模型名称</th>
                  <th className="text-left px-4 py-2.5 font-medium">类型</th>
                  <th className="text-right px-4 py-2.5 font-medium">输入价格/百万Token</th>
                  <th className="text-right px-4 py-2.5 font-medium">输出价格/百万Token</th>
                  <th className="text-right px-4 py-2.5 font-medium">最大 Tokens</th>
                  <th className="text-center px-4 py-2.5 font-medium">默认</th>
                </tr>
              </thead>
              <tbody>
                {models.map((m) => (
                  <tr key={m.id} className="border-t hover:bg-muted/30">
                    <td className="px-4 py-2 font-medium">{m.model_name}</td>
                    <td className="px-4 py-2">{m.model_type}</td>
                    <td className="px-4 py-2 text-right">
                      {m.input_price_per_m != null ? `¥${m.input_price_per_m}` : "-"}
                    </td>
                    <td className="px-4 py-2 text-right">
                      {m.output_price_per_m != null ? `¥${m.output_price_per_m}` : "-"}
                    </td>
                    <td className="px-4 py-2 text-right">{m.max_tokens?.toLocaleString() || "-"}</td>
                    <td className="px-4 py-2 text-center">
                      {m.is_default ? "✓" : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
