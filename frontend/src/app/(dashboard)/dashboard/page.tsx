import Link from "next/link";

const features = [
  { href: "/chat", title: "智能咨询", desc: "AI法律咨询助手，基于法律法规和案例提供专业分析", icon: "💬" },
  { href: "/calculator", title: "赔偿计算", desc: "违法解除、加班费、年休假、工伤赔偿一键计算", icon: "🧮" },
  { href: "/knowledge", title: "知识库", desc: "检索法律法规、判例文书，获取专业法律知识", icon: "📚" },
];

export default function DashboardPage() {
  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">欢迎使用律智通</h1>
        <p className="text-muted-foreground mt-2">专业律师AI助手平台</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((f) => (
          <Link
            key={f.href}
            href={f.href}
            className="block rounded-lg border p-6 hover:shadow-md transition-shadow"
          >
            <span className="text-3xl">{f.icon}</span>
            <h2 className="mt-3 text-lg font-semibold">{f.title}</h2>
            <p className="mt-1 text-sm text-muted-foreground">{f.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
