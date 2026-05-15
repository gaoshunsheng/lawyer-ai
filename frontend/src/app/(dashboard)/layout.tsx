"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";

const navItems = [
  { href: "/dashboard", label: "概览", icon: "📊" },
  { href: "/chat", label: "智能咨询", icon: "💬" },
  { href: "/cases", label: "案件管理", icon: "📋" },
  { href: "/documents", label: "文书中心", icon: "📝" },
  { href: "/calculator", label: "赔偿计算", icon: "🧮" },
  { href: "/knowledge", label: "知识库", icon: "📚" },
  { href: "/token-usage", label: "Token 监控", icon: "📈" },
  { href: "/settings", label: "设置", icon: "⚙️" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

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
        <div className="border-t p-3 space-y-2">
          {user && (
            <div className="flex items-center gap-2 px-1">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-medium">
                {(user.real_name || user.username).charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user.real_name || user.username}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent/50 hover:text-foreground transition-colors text-left"
          >
            退出登录
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
