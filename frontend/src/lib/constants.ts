export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || "律智通";

export const ROLES = {
  PLATFORM_ADMIN: "platform_admin",
  TENANT_ADMIN: "tenant_admin",
  DEPT_ADMIN: "dept_admin",
  LAWYER: "lawyer",
  ASSISTANT: "assistant",
} as const;

export const ROLE_LABELS: Record<string, string> = {
  platform_admin: "平台管理员",
  tenant_admin: "律所管理员",
  dept_admin: "部门管理员",
  lawyer: "律师",
  assistant: "律师助理",
};
