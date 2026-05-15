"use client";

import { useEffect } from "react";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface AttachmentPreview {
  filename: string;
  parsed_text: string;
}

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

  const handleAttachmentUpload = async (
    sid: string,
    file: File,
    authToken: string
  ): Promise<AttachmentPreview> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/chat/sessions/${sid}/attachments`, {
      method: "POST",
      headers: { Authorization: `Bearer ${authToken}` },
      body: formData,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || `上传失败: ${res.status}`);
    }
    return res.json();
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-full text-muted-foreground">加载中...</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      <MessageInput
        onSend={sendMessage}
        isStreaming={isStreaming}
        onStop={stopStreaming}
        sessionId={sessionId}
        token={token}
        onAttachmentUpload={handleAttachmentUpload}
      />
    </div>
  );
}
