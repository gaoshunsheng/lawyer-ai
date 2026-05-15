"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { TRIAL_MODES, TRIAL_ROLES } from "@/lib/constants";
import type { TrialSimulation, TrialRound } from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface StrategyReport {
  plaintiff_strengths?: string[];
  defendant_strengths?: string[];
  key_arguments?: string[];
  recommendations?: string[];
  [key: string]: unknown;
}

export default function TrialSimulationPage({
  params,
}: {
  params: { id: string };
}) {
  const { token } = useAuth();
  const router = useRouter();
  const { id } = params;

  const [simulation, setSimulation] = useState<TrialSimulation | null>(null);
  const [rounds, setRounds] = useState<TrialRound[]>([]);
  const [report, setReport] = useState<StrategyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [inputValue, setInputValue] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [ending, setEnding] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fetchSimulation = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<TrialSimulation>(`/trial/${id}`, token);
      setSimulation(data);
    } catch {
      // handled silently
    }
  }, [token, id]);

  const fetchRounds = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<TrialRound[]>(`/trial/${id}/rounds`, token);
      setRounds(data);
    } catch {
      // handled silently
    }
  }, [token, id]);

  const fetchReport = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<StrategyReport>(
        `/trial/${id}/report`,
        token
      );
      setReport(data);
    } catch {
      // handled silently
    }
  }, [token, id]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await Promise.all([fetchSimulation(), fetchRounds()]);
      setLoading(false);
    };
    load();
  }, [fetchSimulation, fetchRounds]);

  // Fetch report when simulation is completed
  useEffect(() => {
    if (simulation?.status === "completed") {
      fetchReport();
    }
  }, [simulation?.status, fetchReport]);

  // Auto-scroll to bottom when rounds change or streaming
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [rounds, streamingContent]);

  const handleSend = async () => {
    if (!token || !inputValue.trim() || isStreaming) return;

    const content = inputValue.trim();
    setInputValue("");
    setIsStreaming(true);
    setStreamingContent("");

    try {
      abortRef.current = new AbortController();
      const res = await fetch(`${API_BASE}/trial/${id}/respond`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
        signal: abortRef.current.signal,
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value, { stream: true });
        const lines = text.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") break;
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                fullContent += parsed.content;
                setStreamingContent(fullContent);
              }
            } catch {
              // skip malformed JSON
            }
          }
        }
      }

      // Refetch rounds after stream completes
      await fetchRounds();
      await fetchSimulation();
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        console.error("发送失败:", err);
      }
    } finally {
      setIsStreaming(false);
      setStreamingContent("");
      abortRef.current = null;
    }
  };

  const handleEnd = async () => {
    if (!token || ending) return;
    setEnding(true);
    try {
      const data = await api.post<TrialSimulation>(
        `/trial/${id}/end`,
        {},
        token
      );
      setSimulation(data);
      await fetchReport();
    } catch (err) {
      alert(err instanceof Error ? err.message : "操作失败");
    } finally {
      setEnding(false);
    }
  };

  const strengthBadge = (strength: string | null) => {
    if (!strength) return null;
    const map: Record<string, string> = {
      strong: "bg-green-100 text-green-700",
      medium: "bg-yellow-100 text-yellow-700",
      weak: "bg-red-100 text-red-700",
    };
    const labelMap: Record<string, string> = {
      strong: "强",
      medium: "中",
      weak: "弱",
    };
    return (
      <span
        className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${map[strength] || "bg-gray-100 text-gray-700"}`}
      >
        论证强度: {labelMap[strength] || strength}
      </span>
    );
  };

  const roleBadge = (role: string) => {
    const isAI = role === "ai" || role === "judge";
    return (
      <span
        className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${isAI ? "bg-purple-100 text-purple-700" : "bg-primary/10 text-primary"}`}
      >
        {TRIAL_ROLES[role] || role}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      </div>
    );
  }

  if (!simulation) {
    return (
      <div className="p-6">
        <p className="text-center text-muted-foreground py-8">模拟不存在</p>
      </div>
    );
  }

  const isActive = simulation.status === "active";

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/trial")}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            &larr; 返回庭审模拟
          </button>
          <div className="h-4 w-px bg-border" />
          <div>
            <h1 className="text-lg font-semibold">
              {TRIAL_MODES[simulation.mode] || simulation.mode}
            </h1>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs text-muted-foreground">
                角色: {TRIAL_ROLES[simulation.role] || simulation.role}
              </span>
              <span className="text-xs text-muted-foreground">
                轮次: {simulation.rounds_completed}
              </span>
              {isActive ? (
                <span className="inline-block rounded-full px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700">
                  进行中
                </span>
              ) : (
                <span className="inline-block rounded-full px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700">
                  已完成
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isActive && (
            <button
              onClick={handleEnd}
              disabled={ending}
              className="rounded-md border px-4 py-2 text-sm hover:bg-accent disabled:opacity-50"
            >
              {ending ? "结束中..." : "结束模拟"}
            </button>
          )}
          <button
            onClick={() => router.push("/trial")}
            className="rounded-md border px-4 py-2 text-sm hover:bg-accent"
          >
            返回列表
          </button>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {/* Rounds */}
          {rounds.map((round) => {
            const isUser = round.role === simulation.role;
            return (
              <div
                key={round.id}
                className={`flex ${isUser ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-4 space-y-2 ${
                    isUser ? "bg-primary/10" : "bg-muted"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">
                      第 {round.round_num} 轮
                    </span>
                    {roleBadge(round.role)}
                    {!isUser && strengthBadge(round.argument_strength)}
                  </div>
                  <div className="text-sm whitespace-pre-wrap">
                    {round.content}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Streaming content */}
          {isStreaming && streamingContent && (
            <div className="flex justify-start">
              <div className="max-w-[70%] rounded-lg bg-muted p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">回复中</span>
                  <span className="inline-block rounded-full px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-700">
                    AI
                  </span>
                </div>
                <div className="text-sm whitespace-pre-wrap">
                  {streamingContent}
                  <span className="animate-pulse">|</span>
                </div>
              </div>
            </div>
          )}

          {/* Strategy Report (when completed) */}
          {simulation.status === "completed" && report && (
            <div className="pt-4 space-y-4">
              <h2 className="text-lg font-semibold border-b pb-2">
                策略分析报告
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Plaintiff Strengths */}
                {report.plaintiff_strengths &&
                  report.plaintiff_strengths.length > 0 && (
                    <div className="rounded-lg border p-5 space-y-3">
                      <h3 className="font-medium text-sm">原告方优势</h3>
                      <ul className="space-y-1.5">
                        {report.plaintiff_strengths.map((s, i) => (
                          <li
                            key={i}
                            className="text-sm text-muted-foreground flex gap-2"
                          >
                            <span className="text-green-500 shrink-0">+</span>
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                {/* Defendant Strengths */}
                {report.defendant_strengths &&
                  report.defendant_strengths.length > 0 && (
                    <div className="rounded-lg border p-5 space-y-3">
                      <h3 className="font-medium text-sm">被告方优势</h3>
                      <ul className="space-y-1.5">
                        {report.defendant_strengths.map((s, i) => (
                          <li
                            key={i}
                            className="text-sm text-muted-foreground flex gap-2"
                          >
                            <span className="text-blue-500 shrink-0">+</span>
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                {/* Key Arguments */}
                {report.key_arguments && report.key_arguments.length > 0 && (
                  <div className="rounded-lg border p-5 space-y-3">
                    <h3 className="font-medium text-sm">核心争议焦点</h3>
                    <ul className="space-y-1.5">
                      {report.key_arguments.map((a, i) => (
                        <li
                          key={i}
                          className="text-sm text-muted-foreground flex gap-2"
                        >
                          <span className="text-yellow-500 shrink-0">*</span>
                          {a}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {report.recommendations &&
                  report.recommendations.length > 0 && (
                    <div className="rounded-lg border p-5 space-y-3">
                      <h3 className="font-medium text-sm">策略建议</h3>
                      <ul className="space-y-1.5">
                        {report.recommendations.map((r, i) => (
                          <li
                            key={i}
                            className="text-sm text-muted-foreground flex gap-2"
                          >
                            <span className="text-purple-500 shrink-0">
                              {i + 1}.
                            </span>
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
              </div>
            </div>
          )}

          {simulation.status === "completed" && !report && (
            <div className="pt-4">
              <p className="text-center text-muted-foreground py-8">
                正在生成策略报告...
              </p>
            </div>
          )}
        </div>

        {/* Input area (only when active) */}
        {isActive && (
          <div className="border-t px-6 py-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="输入你的论述..."
                disabled={isStreaming}
                className="flex-1 rounded-md border px-3 py-2 text-sm bg-background disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={isStreaming || !inputValue.trim()}
                className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {isStreaming ? "回复中..." : "发送"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
