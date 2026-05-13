"use client";

import { useEffect } from "react";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";

interface ChatInterfaceProps {
  sessionId: string;
  token?: string;
}

export function ChatInterface({ sessionId, token }: ChatInterfaceProps) {
  const { messages, isLoading, isStreaming, loadMessages, sendMessage, stopStreaming } = useChat(
    sessionId,
    token
  );

  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  if (isLoading) {
    return <div className="flex items-center justify-center h-full text-muted-foreground">加载中...</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      <MessageInput onSend={sendMessage} isStreaming={isStreaming} onStop={stopStreaming} />
    </div>
  );
}
