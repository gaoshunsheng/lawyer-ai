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

export const CASE_TYPES: Record<string, string> = {
  labor_contract: "劳动合同",
  wage: "工资报酬",
  injury: "工伤",
  social_insurance: "社会保险",
  termination: "解除终止",
  discrimination: "歧视",
  other: "其他",
};

export const CASE_STATUSES: Record<string, string> = {
  pending: "待处理",
  in_progress: "处理中",
  filed: "已立案",
  hearing: "庭审中",
  mediating: "调解中",
  closed: "已结案",
  archived: "已归档",
  cancelled: "已撤销",
};

export const EVIDENCE_TYPES: Record<string, string> = {
  contract: "合同",
  chat_record: "聊天记录",
  photo: "照片",
  video: "视频",
  audio: "录音",
  document: "文档",
  other: "其他",
};

export const DOC_CATEGORIES: Record<string, string> = {
  "申请类": "申请类",
  "起诉类": "起诉类",
  "答辩类": "答辩类",
  "函件类": "函件类",
  "协议类": "协议类",
  "证据类": "证据类",
  "代理类": "代理类",
  "通知类": "通知类",
};

export const DOC_STATUSES: Record<string, string> = {
  draft: "草稿",
  generating: "生成中",
  completed: "已完成",
  exported: "已导出",
};
