"use client";

import { useState } from "react";

interface FeedbackFormProps {
  messageId: string;
  onSubmit: (feedback: {
    overall_positive: boolean;
    law_accuracy_score?: number;
    analysis_depth_score?: number;
    practical_value_score?: number;
    text_feedback?: string;
  }) => void;
}

export function FeedbackForm({ messageId, onSubmit }: FeedbackFormProps) {
  const [isPositive, setIsPositive] = useState<boolean | null>(null);
  const [scores, setScores] = useState({ law: 0, depth: 0, value: 0 });
  const [textFeedback, setTextFeedback] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (isPositive === null) return;
    onSubmit({
      overall_positive: isPositive,
      ...(scores.law > 0 ? { law_accuracy_score: scores.law } : {}),
      ...(scores.depth > 0 ? { analysis_depth_score: scores.depth } : {}),
      ...(scores.value > 0 ? { practical_value_score: scores.value } : {}),
      ...(textFeedback.trim() ? { text_feedback: textFeedback.trim() } : {}),
    });
    setSubmitted(true);
  };

  if (submitted) {
    return <p className="text-sm text-muted-foreground">感谢您的反馈！</p>;
  }

  return (
    <div className="mt-3 border-t pt-3 space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-sm">回答是否有帮助？</span>
        <button
          onClick={() => setIsPositive(true)}
          className={`px-3 py-1 rounded text-sm ${isPositive === true ? "bg-green-100 text-green-700" : "bg-muted"}`}
        >
          👍 有帮助
        </button>
        <button
          onClick={() => setIsPositive(false)}
          className={`px-3 py-1 rounded text-sm ${isPositive === false ? "bg-red-100 text-red-700" : "bg-muted"}`}
        >
          👎 没帮助
        </button>
      </div>

      {isPositive !== null && (
        <>
          <div className="space-y-2">
            {[
              { key: "law" as const, label: "法条准确性" },
              { key: "depth" as const, label: "分析深度" },
              { key: "value" as const, label: "实用价值" },
            ].map(({ key, label }) => (
              <div key={key} className="flex items-center gap-2">
                <span className="text-sm w-20">{label}</span>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setScores((prev) => ({ ...prev, [key]: star }))}
                      className={`text-lg ${scores[key] >= star ? "text-yellow-500" : "text-gray-300"}`}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <textarea
            value={textFeedback}
            onChange={(e) => setTextFeedback(e.target.value)}
            placeholder="补充反馈 (可选)..."
            className="w-full rounded border px-3 py-2 text-sm resize-none"
            rows={2}
          />

          <button
            onClick={handleSubmit}
            className="rounded bg-primary px-4 py-1.5 text-sm text-primary-foreground hover:bg-primary/90"
          >
            提交反馈
          </button>
        </>
      )}
    </div>
  );
}
