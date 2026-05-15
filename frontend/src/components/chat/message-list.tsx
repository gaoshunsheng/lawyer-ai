"use client";

import { useEffect, useRef } from "react";
import { MessageItem } from "./message-item";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  is_follow_up?: boolean;
  attachments?: Record<string, unknown>;
}

export function MessageList({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="text-center">
            <p className="text-lg font-medium">律智通 - AI法律助手</p>
            <p className="mt-2 text-sm">输入您的法律问题开始咨询</p>
          </div>
        </div>
      )}
      {messages.map((msg) => (
        <MessageItem
          key={msg.id}
          role={msg.role}
          content={msg.content}
          is_follow_up={msg.is_follow_up}
          attachments={msg.attachments}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
