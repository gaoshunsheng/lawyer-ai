import { ChatInterface } from "@/components/chat/chat-interface";

export default async function ChatSessionPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = await params;
  return <ChatInterface sessionId={sessionId} />;
}
