export interface User {
  id: string;
  username: string;
  email: string;
  real_name: string | null;
  role: "platform_admin" | "tenant_admin" | "dept_admin" | "lawyer" | "assistant";
  tenant_id: string;
  department_id: string | null;
  avatar_url: string | null;
  status: string;
}

export interface Tenant {
  id: string;
  name: string;
  plan: "free" | "pro" | "team" | "enterprise";
  status: string;
}

export interface Department {
  id: string;
  tenant_id: string;
  parent_id: string | null;
  name: string;
  path: string | null;
  level: number;
  children?: Department[];
}

export interface ChatSession {
  id: string;
  title: string | null;
  status: string;
  case_id?: string;
  follow_up_count?: number;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  tokens_used: number | null;
  is_follow_up?: boolean;
  attachments?: Record<string, unknown>;
  created_at: string;
}

export interface Law {
  id: string;
  title: string;
  law_type: string;
  promulgating_body: string | null;
  effective_date: string | null;
  status: string;
}

export interface LawArticle {
  id: string;
  law_id: string;
  article_number: string;
  content: string;
}

export interface PrecedentCase {
  id: string;
  case_name: string;
  case_type: string | null;
  court: string | null;
  judgment_date: string | null;
  result: string | null;
  summary: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  real_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface CalculationRequest {
  calc_type: "illegal_termination" | "overtime" | "annual_leave" | "work_injury";
  params: Record<string, unknown>;
}

export interface CalculationResult {
  result: number;
  breakdown: Record<string, unknown>;
  basis: string[];
  steps: string[];
}

export interface FeedbackRequest {
  message_id: string;
  overall_positive: boolean;
  law_accuracy_score?: number;
  analysis_depth_score?: number;
  practical_value_score?: number;
  text_feedback?: string;
}

export interface PersonInfo {
  name: string;
  id_number: string;
  contact: string;
}

export interface CaseItem {
  id: string;
  case_number: string;
  title: string;
  case_type: string;
  status: string;
  plaintiff: PersonInfo;
  defendant: PersonInfo;
  claim_amount: number | null;
  dispute_focus: string[] | null;
  lawyer_id: string;
  assistant_id: string | null;
  tenant_id: string;
  gantt_data: Record<string, unknown> | null;
  ai_analysis: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface CaseListResponse {
  items: CaseItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface EvidenceItem {
  id: string;
  case_id: string;
  tenant_id: string;
  title: string;
  evidence_type: string;
  file_url: string | null;
  file_size: number | null;
  file_type: string | null;
  description: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface TimelineItem {
  id: string;
  case_id: string;
  event_type: string;
  title: string;
  description: string | null;
  event_date: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CaseCreateRequest {
  title: string;
  case_type: string;
  plaintiff: PersonInfo;
  defendant: PersonInfo;
  claim_amount?: number;
  dispute_focus?: string[];
  assistant_id?: string;
}

export interface TemplateItem {
  id: string;
  name: string;
  doc_type: string;
  content_template: string;
  variables_schema: { variables: { name: string; label: string; type: string; required: boolean; default?: string }[] };
  category: string;
  sort_order: number;
  is_system: boolean;
  tenant_id: string | null;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  case_id: string | null;
  tenant_id: string;
  user_id: string;
  title: string;
  doc_type: string;
  template_id: string | null;
  content: Record<string, unknown> | null;
  variables: Record<string, unknown> | null;
  status: string;
  version: number;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface FavoriteItem {
  id: string;
  user_id: string;
  target_type: "law" | "case" | "article";
  target_id: string;
  notes: string | null;
  created_at: string;
}

// ── Phase 3 Types ──

// Trial Simulation
export interface TrialSimulation {
  id: string;
  case_id: string;
  mode: string;
  role: string;
  status: string;
  rounds_completed: number;
  strategy_report: Record<string, unknown> | null;
  created_at: string;
}

export interface TrialRound {
  id: string;
  simulation_id: string;
  round_num: number;
  role: string;
  content: string;
  argument_strength: string | null;
  evaluation: Record<string, unknown> | null;
}

// Gantt Chart
export interface GanttNode {
  id: string;
  title: string;
  type: string;
  start: string;
  end: string;
  assignee_id?: string;
  status?: string;
  progress?: number;
  color?: string;
}

export interface GanttDependency {
  from: string;
  to: string;
  type: string;
}

export interface GanttData {
  nodes: GanttNode[];
  dependencies: GanttDependency[];
}

// Reports
export interface CaseTypeStat {
  type: string;
  count: number;
  amount: number;
}

export interface CaseStatusStat {
  status: string;
  count: number;
}

export interface CaseOverview {
  total: number;
  by_type: CaseTypeStat[];
  by_status: CaseStatusStat[];
  avg_duration_days: number;
  win_rate: number;
  total_claim_amount: number;
}

export interface TrendPeriod {
  period: string;
  total: number;
  by_type: Record<string, number>;
  avg_amount: number;
}

export interface LawyerStat {
  user_id: string;
  name: string;
  total_cases: number;
  win_rate: number;
  avg_satisfaction: number;
  total_claim_amount: number;
}
