"use client";

interface MessageItemProps {
  role: "user" | "assistant" | "system";
  content: string;
  is_follow_up?: boolean;
  attachments?: Record<string, unknown>;
}

export function MessageItem({ role, content, is_follow_up, attachments }: MessageItemProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        <div className="flex flex-wrap items-center gap-2 mb-1">
          {is_follow_up && (
            <span className="inline-block rounded-full px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700">
              追问
            </span>
          )}
          {attachments && (
            <span className="text-xs text-muted-foreground">
              📎 {String(attachments.filename || "附件")}
            </span>
          )}
        </div>
        <div className="whitespace-pre-wrap text-sm leading-relaxed">{content}</div>
      </div>
    </div>
  );
}
