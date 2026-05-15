"use client";

import { useParams, useRouter } from "next/navigation";
import { LawDetail } from "@/components/knowledge/law-detail";

export default function LawDetailPage() {
  const { lawId } = useParams<{ lawId: string }>();
  const router = useRouter();

  return (
    <div className="p-6 space-y-4">
      <button
        onClick={() => router.push("/knowledge/laws")}
        className="text-sm text-muted-foreground hover:text-foreground"
      >
        &larr; 返回法规列表
      </button>
      <LawDetail lawId={lawId} />
    </div>
  );
}
