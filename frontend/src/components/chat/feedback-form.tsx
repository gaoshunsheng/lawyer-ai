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

const StarRating = ({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) => (
  <div className="flex items-center gap-2">
    <span className="text-xs text-muted-foreground w-20">{label}</span>
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          className={`text-lg ${star <= value ? "text-yellow-400" : "text-gray-300"} hover:text-yellow-400 transition-colors`}
        >
          ★
        </button>
      ))}
    </div>
  </div>
);

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
        <div className="space-y-2 py-3 border-t">
          <p className="text-xs text-muted-foreground">请对本次回复进行评价（可选）</p>
          <StarRating label="法条准确性" value={scores.law} onChange={(v) => setScores((s) => ({ ...s, law: v }))} />
          <StarRating label="分析深度" value={scores.depth} onChange={(v) => setScores((s) => ({ ...s, depth: v }))} />
          <StarRating label="实用价值" value={scores.value} onChange={(v) => setScores((s) => ({ ...s, value: v }))} />
          <textarea
            value={textFeedback}
            onChange={(e) => setTextFeedback(e.target.value)}
            maxLength={500}
            rows={3}
            placeholder="补充你的评价（最多500字）..."
            className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-2"
          />
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">{textFeedback.length}/500</span>
            <button
              onClick={handleSubmit}
              disabled={submitted}
              className="rounded-md bg-primary px-4 py-1.5 text-xs text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {submitted ? "已提交" : "提交评价"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
