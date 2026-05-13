"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api-client";
import { useAuth } from "@/providers/auth-provider";
import { ChatInterface } from "@/components/chat/chat-interface";

interface Session {
  id: string;
  title: string | null;
  created_at: string;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const { token } = useAuth();

  const fetchSessions = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<Session[]>("/chat/sessions", token);
      setSessions(data);
    } catch {
      console.error("获取会话列表失败");
    }
  }, [token]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const createNewSession = async () => {
    if (!token) return;
    try {
      const session = await api.post<Session>("/chat/sessions", { title: "新对话" }, token);
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
    } catch (err) {
      console.error("创建会话失败:", err);
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
          <ChatInterface sessionId={activeSessionId} token={token} />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            点击「新对话」开始咨询
          </div>
        )}
      </div>
    </div>
  );
}
