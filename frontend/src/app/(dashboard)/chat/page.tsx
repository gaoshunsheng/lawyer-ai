"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api-client";
import { useAuth } from "@/providers/auth-provider";
import { ChatInterface } from "@/components/chat/chat-interface";
import type { ChatSession } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface CaseItem {
  id: string;
  case_number: string;
  title: string;
  case_type: string;
}

interface CaseListResponse {
  items: CaseItem[];
  total: number;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const { token } = useAuth();

  // Case link state
  const [showCasePicker, setShowCasePicker] = useState(false);
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [linkedCaseId, setLinkedCaseId] = useState<string | null>(null);
  const [linkedCaseName, setLinkedCaseName] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  const fetchSessions = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<ChatSession[]>("/chat/sessions", token);
      setSessions(data);
    } catch {
      console.error("获取会话列表失败");
    }
  }, [token]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  // Sync linked case info when active session changes
  useEffect(() => {
    const session = sessions.find((s) => s.id === activeSessionId);
    if (session?.case_id) {
      setLinkedCaseId(session.case_id);
      const match = cases.find((c) => c.id === session.case_id);
      setLinkedCaseName(match?.title || session.case_id);
    } else {
      setLinkedCaseId(null);
      setLinkedCaseName(null);
    }
  }, [activeSessionId, sessions, cases]);

  const createNewSession = async () => {
    if (!token) return;
    try {
      const session = await api.post<ChatSession>("/chat/sessions", { title: "新对话" }, token);
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
    } catch (err) {
      console.error("创建会话失败:", err);
    }
  };

  // Fetch cases for the picker
  const openCasePicker = async () => {
    if (!token) return;
    setShowCasePicker(true);
    try {
      const data = await api.get<CaseListResponse>("/cases?page=1&page_size=50", token);
      setCases(data.items);
    } catch (err) {
      console.error("获取案件列表失败:", err);
    }
  };

  const linkCase = async (caseId: string) => {
    if (!token || !activeSessionId) return;
    try {
      await api.post(`/chat/sessions/${activeSessionId}/link-case`, { case_id: caseId }, token);
      const caseItem = cases.find((c) => c.id === caseId);
      setLinkedCaseId(caseId);
      setLinkedCaseName(caseItem?.title || caseId);
      setSessions((prev) =>
        prev.map((s) => (s.id === activeSessionId ? { ...s, case_id: caseId } : s))
      );
      setShowCasePicker(false);
    } catch (err) {
      console.error("关联案件失败:", err);
    }
  };

  const unlinkCase = async () => {
    if (!token || !activeSessionId) return;
    try {
      await api.delete(`/chat/sessions/${activeSessionId}/link-case`, token);
      setLinkedCaseId(null);
      setLinkedCaseName(null);
      setSessions((prev) =>
        prev.map((s) => (s.id === activeSessionId ? { ...s, case_id: undefined } : s))
      );
    } catch (err) {
      console.error("取消关联失败:", err);
    }
  };

  const exportChat = async () => {
    if (!token || !activeSessionId) return;
    setIsExporting(true);
    try {
      const res = await fetch(
        `${API_BASE}/chat/sessions/${activeSessionId}/export?format=docx`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error("导出失败");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chat_${activeSessionId}.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("导出失败:", err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar - session list */}
      <div className="w-64 border-r flex flex-col">
        <div className="p-4 border-b">
          <button
            onClick={createNewSession}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
          >
            + 新对话
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => setActiveSessionId(session.id)}
              className={`w-full text-left rounded-md px-3 py-2 text-sm truncate ${
                activeSessionId === session.id ? "bg-accent" : "hover:bg-accent/50"
              }`}
            >
              {session.title || "新对话"}
            </button>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {activeSessionId ? (
          <>
            {/* Session header with case link + export */}
            <div className="flex items-center justify-between border-b px-4 py-2 bg-background">
              <div className="flex items-center gap-2 text-sm">
                <span className="font-medium">
                  {sessions.find((s) => s.id === activeSessionId)?.title || "对话"}
                </span>
                {linkedCaseId ? (
                  <span className="flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                    案件: {linkedCaseName}
                    <button
                      onClick={unlinkCase}
                      className="ml-1 text-blue-400 hover:text-blue-700"
                      title="取消关联"
                    >
                      ✕
                    </button>
                  </span>
                ) : null}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={linkedCaseId ? unlinkCase : openCasePicker}
                  className="rounded-md border px-3 py-1.5 text-xs hover:bg-accent"
                >
                  {linkedCaseId ? "取消关联" : "关联案件"}
                </button>
                <button
                  onClick={exportChat}
                  disabled={isExporting}
                  className="rounded-md border px-3 py-1.5 text-xs hover:bg-accent disabled:opacity-50"
                >
                  {isExporting ? "导出中..." : "导出"}
                </button>
              </div>
            </div>

            {/* Case picker overlay */}
            {showCasePicker && (
              <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/30">
                <div className="w-96 max-h-[70vh] rounded-lg border bg-background shadow-lg flex flex-col">
                  <div className="flex items-center justify-between border-b px-4 py-3">
                    <span className="text-sm font-medium">选择案件</span>
                    <button
                      onClick={() => setShowCasePicker(false)}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="flex-1 overflow-y-auto p-2">
                    {cases.length === 0 ? (
                      <div className="py-8 text-center text-sm text-muted-foreground">
                        暂无可关联案件
                      </div>
                    ) : (
                      cases.map((c) => (
                        <button
                          key={c.id}
                          onClick={() => linkCase(c.id)}
                          className="w-full text-left rounded-md px-3 py-2 text-sm hover:bg-accent mb-1"
                        >
                          <div className="font-medium truncate">{c.title}</div>
                          <div className="text-xs text-muted-foreground">
                            {c.case_number} · {c.case_type}
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="flex-1 min-h-0">
              <ChatInterface sessionId={activeSessionId} token={token!} />
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            点击「新对话」开始咨询
          </div>
        )}
      </div>
    </div>
  );
}
