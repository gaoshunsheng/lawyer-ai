"use client";

import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/40">
      <div className="w-full max-w-md space-y-6 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">律智通</h1>
          <p className="text-muted-foreground mt-1">专业律师AI助手平台</p>
        </div>
        {children}
      </div>
    </div>
  );
}
