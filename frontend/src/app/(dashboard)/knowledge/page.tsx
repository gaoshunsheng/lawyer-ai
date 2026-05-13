"use client";

import Link from "next/link";

export default function KnowledgePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">法律知识库</h1>
        <p className="text-muted-foreground mt-2">
          检索法律法规、判例文书，获取专业法律知识
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link
          href="/knowledge/laws"
          className="block rounded-lg border p-6 hover:shadow-md transition-shadow"
        >
          <h2 className="text-xl font-semibold">法律法规</h2>
          <p className="text-muted-foreground mt-2">
            检索国家法律、行政法规、司法解释、地方性法规
          </p>
        </Link>

        <Link
          href="/knowledge/cases"
          className="block rounded-lg border p-6 hover:shadow-md transition-shadow"
        >
          <h2 className="text-xl font-semibold">判例文书</h2>
          <p className="text-muted-foreground mt-2">
            检索劳动争议、合同纠纷等典型案例和裁判文书
          </p>
        </Link>
      </div>
    </div>
  );
}
