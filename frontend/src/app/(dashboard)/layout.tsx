"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "概览", icon: "📊" },
  { href: "/chat", label: "智能咨询", icon: "💬" },
  { href: "/calculator", label: "赔偿计算", icon: "🧮" },
  { href: "/knowledge", label: "知识库", icon: "📚" },
  { href: "/settings", label: "设置", icon: "⚙️" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen">
      <aside className="w-60 border-r bg-background flex flex-col">
        <div className="h-14 flex items-center px-4 border-b font-bold text-lg">
          律智通
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                pathname === item.href
                  ? "bg-accent text-accent-foreground font-medium"
                  : "text-muted-foreground hover:bg-accent/50"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t">
          <p className="text-xs text-muted-foreground">v0.1.0 · 律智通 AI</p>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
