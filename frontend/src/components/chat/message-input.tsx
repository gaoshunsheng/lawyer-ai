"use client";

import { useState, useRef } from "react";

interface AttachmentPreview {
  filename: string;
  parsed_text: string;
}

interface MessageInputProps {
  onSend: (content: string, attachmentText?: string) => void;
  isStreaming: boolean;
  onStop: () => void;
  sessionId?: string;
  token?: string;
  onAttachmentUpload?: (sessionId: string, file: File, token: string) => Promise<AttachmentPreview>;
}

export function MessageInput({ onSend, isStreaming, onStop, sessionId, token, onAttachmentUpload }: MessageInputProps) {
  const [input, setInput] = useState("");
  const [attachment, setAttachment] = useState<AttachmentPreview | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if ((!input.trim() && !attachment) || isStreaming) return;
    onSend(input, attachment?.parsed_text);
    setInput("");
    setAttachment(null);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !sessionId || !token || !onAttachmentUpload) return;

    setIsUploading(true);
    try {
      const result = await onAttachmentUpload(sessionId, file, token);
      setAttachment(result);
    } catch (err) {
      console.error("上传附件失败:", err);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="border-t p-4">
      {attachment && (
        <div className="mb-2 flex items-center gap-2 rounded-md border bg-muted/50 px-3 py-2 text-sm">
          <span className="truncate">📎 {attachment.filename}</span>
          <button
            onClick={() => setAttachment(null)}
            className="ml-auto text-muted-foreground hover:text-foreground shrink-0"
          >
            ✕
          </button>
        </div>
      )}
      <div className="flex gap-2">
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileSelect}
          accept=".pdf,.doc,.docx,.txt"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading || !sessionId}
          className="rounded-md border px-3 py-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
          title="上传附件"
        >
          {isUploading ? "..." : "📎"}
        </button>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          placeholder="输入法律问题... (Enter发送, Shift+Enter换行)"
          className="flex-1 rounded-md border px-4 py-2 resize-none min-h-[44px] max-h-[200px]"
          rows={1}
        />
        {isStreaming ? (
          <button
            onClick={onStop}
            className="rounded-md bg-destructive px-4 py-2 text-destructive-foreground hover:bg-destructive/90"
          >
            停止
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim() && !attachment}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            发送
          </button>
        )}
      </div>
    </div>
  );
}
