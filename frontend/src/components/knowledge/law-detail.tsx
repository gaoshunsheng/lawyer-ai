"use client";

import { useEffect, useState } from "react";

interface LawArticle {
  id: string;
  article_number: string;
  content: string;
  chapter: string | null;
}

interface LawDetail {
  id: string;
  title: string;
  law_type: string;
  promulgating_body: string | null;
  effective_date: string | null;
  status: string;
  full_text: string;
  articles: LawArticle[];
}

export function LawDetail({ lawId }: { lawId: string }) {
  const [law, setLaw] = useState<LawDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLaw = async () => {
      try {
        const res = await fetch(`/api/v1/knowledge/laws/${lawId}`);
        const data = await res.json();
        setLaw(data);
      } catch {
        console.error("获取法规详情失败");
      } finally {
        setLoading(false);
      }
    };
    fetchLaw();
  }, [lawId]);

  if (loading) return <div className="py-8 text-center text-muted-foreground">加载中...</div>;
  if (!law) return <div className="py-8 text-center text-muted-foreground">法规不存在</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{law.title}</h1>
        <div className="mt-2 flex gap-4 text-sm text-muted-foreground">
          {law.promulgating_body && <span>{law.promulgating_body}</span>}
          {law.effective_date && <span>施行日期: {law.effective_date}</span>}
          <span>状态: {law.status === "effective" ? "有效" : law.status}</span>
        </div>
      </div>

      {law.articles.length > 0 ? (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">条款列表</h2>
          {law.articles.map((article) => (
            <div key={article.id} className="rounded-lg border p-4">
              {article.chapter && (
                <p className="text-sm font-medium text-primary mb-1">{article.chapter}</p>
              )}
              <h3 className="font-medium">{article.article_number}</h3>
              <p className="mt-2 text-sm leading-relaxed whitespace-pre-wrap">{article.content}</p>
            </div>
          ))}
        </div>
      ) : (
        <div>
          <h2 className="text-lg font-semibold mb-4">全文</h2>
          <div className="rounded-lg border p-6 text-sm leading-relaxed whitespace-pre-wrap">
            {law.full_text}
          </div>
        </div>
      )}
    </div>
  );
}
