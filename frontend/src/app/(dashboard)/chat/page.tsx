"use client";

import { useState, useEffect } from "react";
import { ChatInterface } from "@/components/chat/chat-interface";

interface Session {
  id: string;
  title: string | null;
  created_at: string;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await fetch("/api/v1/chat/sessions");
        const data = await res.json();
        setSessions(data);
        if (data.length > 0 && !activeSessionId) {
          setActiveSessionId(data[0].id);
        }
      } catch {
        console.error("获取会话列表失败");
      }
    };
    fetchSessions();
  }, [activeSessionId]);

  const createNewSession = async () => {
    try {
      const res = await fetch("/api/v1/chat/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "新对话" }),
      });
      const session = await res.json();
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
    } catch {
      console.error("创建会话失败");
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
          <ChatInterface sessionId={activeSessionId} />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            点击「新对话」开始咨询
          </div>
        )}
      </div>
    </div>
  );
}
